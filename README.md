## Speech To Text app with Flask

A Speech-To-Text app with Flask in which we can upload a video or an audio file and can get transcripts of the speech inthe file we upload.

##### How it works

Once we upload a video file, it takes the audio from the video with the information of the file such as sampling rate by using <strong><a href="https://kkroening.github.io/ffmpeg-python/" target="_blank">ffmpeg-python</a></strong>, which is a wrapper of <strong><a href="https://ffmpeg.org/ffmpeg.html" target="_blank">ffmpeg</a></strong>.
Based on the information, it converts the audio to a 1-D Numpy array which is fed into the DeepSpeech model which trained by machine learning
techniques based on <strong><a href="https://arxiv.org/abs/1412.5567" target="_blank">Baidu's Deep Speech research paper</a></strong>.
The output from the DeepSpeech model is then fed into a language model in order to improve the prediction accuracy.

For more infomation, please visit <strong><a href="https://boblef.github.io/" target="_blank">my site</a></strong></strong>.

## How to use

1. Clone this repository to your local.

   ```
   git clone https://github.com/boblef/auto_transcript
   ```

2. Set up the environment, and run the application<br>
   You can set up the environment in which we run the Flask application either by using Docker or by creating a conda or pip env by yourself.
   <strong>Strongly recommend to use Docker. Otherwise, you need to install `Sox` and `ffmpeg` to your machine.</strong>

- Docker
  Build a container
  ```
  docker build -t auto_transcript:latest .
  ```
  Run the image
  ```
  docker run -d -p 5000:5000 auto_transcript:latest
  ```
  Open up your browser, and copy and paste the link below. The application is supposed to start.
  ```
  http://localhost:5000/
  ```

3. Upload a file
   There are sample audio files in the `samples/`. You can grab one of them or upload a `mp4` file you have.
   <br>
4. Click "Create transcripts"
   After you click the button, it will take some time to print the transcripts. (About a minute for 30sec length video)
   <br>
5. Once the transcripts printed out, there is a button that appeared where you can download a `zip` file that contains a `JSON` which includes a list of words with start time and duration and a `text` file that keeps a sentence of words concatenated with white space.

## Further Work

- Add another feature that detects specific motions of the user and put marks on the sequence of frames so that the user will be able to find easily where they want to cut.
- Deploy as a C++ software since I want to create a software with C++.

## Reference

- [Deep Speech: Scaling up end-to-end speech recognition](https://arxiv.org/abs/1412.5567)
- [ffmpeg-python](https://kkroening.github.io/ffmpeg-python/)
