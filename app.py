from flask import Flask, render_template, request
from lib.DeepSpeech import DeepSpeech

app = Flask(__name__, static_folder='static')

STT_MODEL_PATH = "model/deepspeech-0.7.4-models.pbmm"
SCORER_MODEL_PATH = "model/deepspeech-0.7.4-models.scorer"
result_json_path = "results/result.json"
UPLOADED_BASE = "static/uploaded/tmp.mp4"

ds = DeepSpeech(model_path=STT_MODEL_PATH,
                scorer_path=SCORER_MODEL_PATH,
                result_json_path=result_json_path,
                )


@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('index.html')


@app.route('/upload_file', methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        f = request.files['file']
        ds.set_file(UPLOADED_BASE)
        f.save(UPLOADED_BASE)
        return render_template('dashboard.html')


@app.route('/process', methods=["GET", "POST"])
def process():
    if request.method == "POST":
        status = request.form["user_request"]
        if status == "top":
            return render_template("index.html")
        else:
            ds.take_audio_info()
            ds.take_audio()
            sentence = ds.speech2text()
            return render_template("dashboard.html", sentence=sentence)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
