from flask import Flask, request, jsonify
import json

app = Flask(__name__)


@app.route('/checkUrl', methods=['POST'])
def hello_world():
    # Get json params here
    json_param = json.loads(request.data)

    # TODO check url here, and fill result to result dict
    result = {}

    # Finally, return result json to client
    return jsonify(result)


if __name__ == '__main__':
    app.run()
