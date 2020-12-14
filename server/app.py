from flask import Flask, request, jsonify, redirect, url_for
from flask_cors import *  # 导入模块
import json
import pickle
import numpy
from part_functions import FeatureGetter


app = Flask(__name__)
CORS(app, supports_credentials=True)  # 设置跨域


@app.route("/redirect_test4", methods=['GET'])
def redirect_test4():
    return "Result"


@app.route("/redirect_test3", methods=['GET'])
def redirect_test3():
    return redirect(url_for("redirect_test4"), code=302)


@app.route("/redirect_test2", methods=['GET'])
def redirect_test2():
    return redirect(url_for("redirect_test3"), code=302)


@app.route("/redirect_test", methods=['GET'])
def redirect_test():
    return redirect(url_for("redirect_test2"), code=302)


@app.route('/checkUrl', methods=['POST'])
def check_url():
    # Get json params here
    json_param = json.loads(request.data)
    print(json_param['url'])

    fg = FeatureGetter(json_param['url'])


    # TODO check url here, and fill result to result dict
    result = {
        "code": 0,
        "msg": "",
        "data": {
            "security": False
        }
    }
    response = jsonify(result)
    # Finally, return result json to client
    return response


if __name__ == '__main__':
    app.run()
