from flask import Flask, render_template, request

app = Flask(__name__, static_folder='static')

UPLOADED_BASE = "static/uploaded/tmp.mp4"


@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('index.html')


@app.route('/upload_file', methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        f = request.files['file']
        f.save(UPLOADED_BASE)
        return render_template('dashboard.html')


@app.route('/process', methods=["GET", "POST"])
def process():
    if request.method == "POST":
        status = request.form["user_request"]
        if status == "top":
            return render_template("index.html")
        else:
            return render_template("dashboard.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
