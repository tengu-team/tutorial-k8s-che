from flask import Flask, Response

app = Flask(__name__)


@app.route('/ping', methods=['GET'])
def ping():
    resp = Response("pang")
    return resp


if __name__ == "__main__":
    app.run(host='0.0.0.0')

