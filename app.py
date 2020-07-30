from deepspeech import Model
import wave
from shlex import quote
import subprocess
import shlex
import numpy as np
import json

MODEL_PATH = "model/deepspeech-0.7.4-models.pbmm"
FILE_PATH = "samples/OSR_us_000_0010_8k.wav"
CANDIDATE_TRANSCRIPTS = 3  # The number of times to trascript

ds = Model(MODEL_PATH)
beam_width = ""


def convert_samplerate(audio_path, desired_sample_rate):
    sox_cmd = 'sox {} --type raw --bits 16 --channels 1 --rate {} --encoding\
         signed-integer --endian little --compression 0.0 --no-dither - '\
    .format(quote(audio_path), desired_sample_rate)
    try:
        output = subprocess.check_output(
            shlex.split(sox_cmd), stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError('SoX returned non-zero status: {}'.format(e.stderr))
    except OSError as e:
        raise OSError(e.errno,
                      'SoX not found, use {}hz files or install it: {}'.format(
                          desired_sample_rate, e.strerror))

    return desired_sample_rate, np.frombuffer(output, np.int16)


def words_from_candidate_transcript(metadata):
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
        # Word boundary is either a space or the last character in the array
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


def metadata_json_output(metadata):
    print("Indide metadata, 1")
    json_result = dict()
    print("Indide metadata, 2")
    json_result["transcripts"] = [{
        "confidence": transcript.confidence,
        "words": words_from_candidate_transcript(transcript),
    } for transcript in metadata.transcripts]
    print("Indide metadata, 3")
    return json.dumps(json_result, indent=4)


if beam_width:
    ds.setBeamWidth(beam_width)

# Get sample rate
desired_sample_rate = ds.sampleRate()

# Open audio file
fin = wave.open(FILE_PATH, 'rb')

# Get frame rate
fs_orig = fin.getframerate()
print("sample rate: ", fs_orig)
if fs_orig != desired_sample_rate:
    print('Warning: original sample rate ({}) is different than {}hz.\
         Resampling might produce erratic speech recognition.'.format(
        fs_orig, desired_sample_rate))
    fs_new, audio = convert_samplerate(FILE_PATH, desired_sample_rate)
else:
    audio = np.frombuffer(fin.readframes(fin.getnframes()), np.int16)

audio_length = fin.getnframes() * (1/fs_orig)
fin.close()

print("Start defining test")
test = ds.sttWithMetadata(
    audio, CANDIDATE_TRANSCRIPTS)
print("Define test")
json_out = metadata_json_output(test)
# json_obj = json.dump(json_out, ensure_ascii=False, indent=4,
#                      sort_keys=True, separators=(',', ': '))

with open('samples/data.json', 'w') as outfile:
    outfile.write(json_out)

# Decode
result = json.loads(json_out)
# # print(json.loads(json_out)["transcripts"][0])
# sentence = [item["word"] for item in result["transcripts"][0]["words"]]
# print(sentence)

# Duration
words = [item["word"]
         for item in result["transcripts"][0]["words"] if item["duration"] > 1]
print(words)
