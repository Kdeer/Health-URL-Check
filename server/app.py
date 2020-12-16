from flask import Flask, request, jsonify, redirect, url_for
from flask_cors import *  # import flask_cors moudle
import json
from part_functions import FeatureGetter
from final_model import get_voting_result

app = Flask(__name__)
CORS(app, supports_credentials=True)  # set cross-domain


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


features = [
    'feature1',
    'feature2',
    'feature3',
    'feature4',
    'feature5',
    'feature6',
    'feature7',
    'feature8',
    'feature10',
    'feature11',
    'feature12',
    'feature13',
    'feature14',
    'feature15',
    'feature16',
    'feature17',
    'feature18',
    'feature19',
    'feature20',
    'feature21',
    'feature22',
    'feature23',
    'feature24',
    'feature25',
    'feature26',
    'feature28',
    'feature30'
]


@app.route('/checkUrl', methods=['POST'])
def check_url():
    # Get json params here
    json_param = json.loads(request.data)
    print(json_param['url'])

    print(json_param)

    # check url here, and fill result to result dict
    fg = FeatureGetter(json_param['url'])
    myFeatures, parameters = json_param['features'], []
    for feature in features:
        if feature not in myFeatures:
            myFeatures[feature] = fg.call_function(feature)
        parameters.append(myFeatures[feature])

    # call ML code
    test_result = get_voting_result([parameters])

    security = False
    if test_result == 1:
        security = True
    result = {
        "code": 0,
        "msg": "",
        "data": {
            "security": security
        }
    }
    response = jsonify(result)
    # Finally, return result json to client
    return response


if __name__ == '__main__':
    app.run()
