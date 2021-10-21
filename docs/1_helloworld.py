# export FLASK_APP = 1_helloworld.py
# flask run
from flask import Flask, request, Response
from flask.json import jsonify

app = Flask(__name__)


@app.route("/addnums", methods=["POST"])
def add_nums():
    resp = {
        "sum": request.get_json()["x"] + request.get_json()["y"],
    }
    return jsonify(resp),200


@app.route('/')
def hello_world():
    return "Hello world"


@app.route('/hello')
def another_hello():
    res_json = {
        "field 1": "value 1",
        "field 2": {
            "nested f1": "nested f1",
            "nested f2": "nested f2"
        }
    }
    return jsonify(res_json)


if __name__ == '__main__':
    app.run(debug=True)
