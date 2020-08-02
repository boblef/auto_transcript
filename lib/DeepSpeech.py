from deepspeech import Model
from shlex import quote
import subprocess
import shlex
import numpy as np
import json
import ffmpeg


class DeepSpeech():
    def __init__(self, model_path, scorer_path, result_json_path,
                 result_txt_path, candidate_transcripts=3, beam_width=None):

        # Path to the Speech-To-Text model
        self.MODEL_PATH = model_path
        # Path to the scorer language mode
        self.SCORER_PATH = scorer_path
        # The number of times to trascript
        self.CANDIDATE_TRANSCRIPTS = candidate_transcripts

        self.result_json_path = result_json_path
        self.result_txt_path = result_txt_path

        self.beam_width = beam_width

        self._setup()

    def _setup(self):
        self.ds = Model(self.MODEL_PATH)  # Declare the model obj
        # Set desired sample rate for STT model.
        self.sample_rate = '16000'

        if self.beam_width:
            self.ds.setBeamWidth(self.beam_width)

        if self.SCORER_PATH:
            self.ds.enableExternalScorer(self.SCORER_PATH)

    def convert_samplerate(self, audio_path, desired_sample_rate):
        sox_cmd = 'sox {} --type raw --bits 16 --channels 1 --rate {}\
                   --encoding signed-integer --endian little\
                   --compression 0.0 --no-dither - '\
        .format(quote(audio_path), desired_sample_rate)
        try:
            output = subprocess.check_output(
                shlex.split(sox_cmd), stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                'SoX returned non-zero status: {}'.format(e.stderr))
        except OSError as e:
            raise OSError(e.errno,
                          'SoX not found, use {}hz files or install it: {}'
                          .format(desired_sample_rate, e.strerror))

        return desired_sample_rate, np.frombuffer(output, np.int16)

    def words_from_candidate_transcript(self, metadata):
        word = ""
        word_list = []
        word_start_time = 0
        # Loop through each character
        for i, token in enumerate(metadata.tokens):
            # Append character to word if it's not a space
            if token.text != " ":
                if len(word) == 0:
                    # Log the start time of the new word
                    word_start_time = token.start_time

                word = word + token.text
            # Word boundary is either a space or the last character in the arr
            if token.text == " " or i == len(metadata.tokens) - 1:
                word_duration = token.start_time - word_start_time

                if word_duration < 0:
                    word_duration = 0

                each_word = dict()
                each_word["word"] = word
                each_word["start_time "] = round(word_start_time, 4)
                each_word["duration"] = round(word_duration, 4)

                word_list.append(each_word)
                # Reset
                word = ""
                word_start_time = 0

        return word_list

    def metadata_json_output(self, metadata):
        json_result = dict()
        json_result["transcripts"] = [{
            "confidence": transcript.confidence,
            "words": self.words_from_candidate_transcript(transcript),
        } for transcript in metadata.transcripts]
        return json.dumps(json_result, indent=4)

    def take_audio_info(self):
        probe = ffmpeg.probe(self.FILE_PATH)
        self.audio_info = next(
            (stream for stream in probe['streams']
             if stream['codec_type'] == 'audio'), None)
        print(self.audio_info)
        return self.audio_info

    def take_audio(self):
        out, err = (
            ffmpeg
            .input(self.FILE_PATH)
            .output('-', format='s16le',
                    acodec='pcm_s16le', ac=1, ar=self.sample_rate)
            .run(capture_stdout=True, capture_stderr=True)
        )
        self.audio = np.frombuffer(out, np.int16)
        return self.audio

    def speech2text(self):
        metadata = self.ds.sttWithMetadata(
            self.audio, self.CANDIDATE_TRANSCRIPTS)
        json_result = self.metadata_json_output(metadata)

        with open(self.result_json_path, 'w') as outfile:
            outfile.write(json_result)

        dict_result = json.loads(json_result)
        word_list = [item["word"]
                     for item in dict_result["transcripts"][0]["words"]]

        sentence = " ".join(word_list)
        self.export2textfile(sentence)
        return sentence

    def export2textfile(self, sentence):
        txt_file = open(self.result_txt_path, "w")
        txt_file.writelines(sentence)
        txt_file.close()

    def set_file(self, filepath):
        self.FILE_PATH = filepath
