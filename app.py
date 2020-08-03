from flask import Flask, render_template, request, send_file
from lib.DeepSpeech import DeepSpeech
import os
import zipfile

app = Flask(__name__, static_folder='static')

STT_MODEL_PATH = "model/deepspeech-0.7.4-models.pbmm"
SCORER_MODEL_PATH = "model/deepspeech-0.7.4-models.scorer"
result_json_path = "results/result.json"
result_txt_path = "results/result.txt"
UPLOADED_BASE = "static/uploaded/tmp.mp4"

ds = DeepSpeech(model_path=STT_MODEL_PATH,
                scorer_path=SCORER_MODEL_PATH,
                result_json_path=result_json_path,
                result_txt_path=result_txt_path
                )

if not os.path.exists(os.getcwd() + "/results"):
    os.mkdir(os.getcwd() + "/results")

if not os.path.exists(os.getcwd() + "static/uploaded"):
    os.mkdir(os.getcwd() + "static/uploaded")


@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('index.html')


@app.route('/upload_file', methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        f = request.files['file']
        ds.set_file(UPLOADED_BASE)
        f.save(UPLOADED_BASE)
        return render_template('dashboard.html', result_status=False)


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
            result_status = True
            return render_template("dashboard.html",
                                   sentence=sentence,
                                   result_status=result_status)


@app.route('/download/', methods=['GET', 'POST'])
def download():
    print("download")
    zipf = zipfile.ZipFile('transcripts.zip', 'w', zipfile.ZIP_DEFLATED)
    zipdir("results/", zipf)
    zipf.close()
    return send_file("transcripts.zip", as_attachment=True)


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
