"""
If you are in the same directory as this file (app.py), you can run run the app using gunicorn:
    
    $ gunicorn --bind 0.0.0.0:<PORT> app:app

gunicorn can be installed via:

    $ pip install gunicorn

"""
import os
import logging
import pickle
import pandas as pd
from flask import Flask, request, jsonify, abort
from logging.config import dictConfig
from comet_ml.api import API


dictConfig({
    "version": 1,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": "flask.log",
            "formatter": "default"
        },
        "console": {
            "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["file", "console"]
    }
    
})
# dataset = '../data/all_new_game_data_with_features.csv'
app = Flask(__name__)
api = API(os.environ.get('COMET_API_KEY'))
# path = f'../data/{dataset}'
model_data = None


@app.before_first_request
def before_first_request():
    """
    Hook to handle any initialization before the first request (e.g. load model,
    setup logging handler, etc.)
    """
    # setup basic logging configuration
    # logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

    # any other initialization before the first request (e.g. load default model)
    global model_data
    model_data = {
        "log" : {
            "file_name":"both.sav",
            "registry_name" : "distance-and-angle-model-1",
            "cols" : [['shot_distance', 'shot_angle']]
        },
        "xgboost" : {
            "file_name":"XGBOOST-baseline.sav",
            "registry_name" : "xgboost-baseline",
            "cols": ['shot_distance_to_goal', 'shot_angle']
        }
    }
    pass



@app.route('/predict', methods=['POST'])
def predict():
    """
    Handles POST requests made to http://IP_ADDRESS:PORT/predict

    Returns predictions
    """

    body = request.get_json()
    data = {
        'shot_distance_to_goal': [body['shot_distance_to_goal']],
        'shot_angle': [body['shot_angle']]
    }
    df = pd.DataFrame(data)
    app.logger.info(body)
    if model_name in model_data.keys():
        response = model.predict_proba(df.values)[0][1]
        app.logger.info(response)
        return jsonify(str(response))
    else:
        app.logger.info("the model is not valid")
        rep = {"message":"the model is not valid"}
        return jsonify(rep)


@app.route('/logs', methods=["GET"])
def logs():
    """Reads data from the log file and returns them as the response"""
    file = open('flask.log', 'r')
    response = file.read().splitlines()
    file.close()
    
    return jsonify(response) 


@app.route('/download_registry_model', methods=['POST'])
def download_registry_model():
    """
    Handles POST requests made to http://IP_ADDRESS:PORT/download_registry_model
    The comet API key should be retrieved from the ${COMET_API_KEY} environment variable.
    Recommend (but not required) json with the schema:
        {
            workspace: (required),
            model: (required),
            version: (required),
            ... (other fields if needed) ...
        }
    
    """
    global model
    global model_name
    model = None
    req_body = request.get_json()
    model_name = req_body['model']
    app.logger.info(req_body)
    if model_name in model_data.keys():
        if os.path.exists(f'model/{model_data[model_name]["file_name"]}'):
            model = pickle.load(open(f'model/{model_data[model_name]["file_name"]}', 'rb'))
            app.logger.info("Model has been changed!")
        else:
            try:
                 api.download_registry_model(workspace="mahmoodhegazy", registry_name=model_data[model_name]["registry_name"], output_path="./model")
                 model = pickle.load(open(f'model/{model_data[model_name]["file_name"]}', 'rb'))
                 app.logger.info("Model has been downloaded!")
            except:
                 app.logger.info("the model is not available")
        
    else:
        msg = {"message":"model is not valid"}
        app.logger.info(msg["message"])
        return jsonify(msg)

    response = 'SUCCESS: '+ model_name + ' is loaded!'
    app.logger.info(response)
    return jsonify(response) 


def clean_log_file():
    open('flask.log', 'w').close()

# Set the port to 8080
port = 8080

# clean the log file
clean_log_file()

# Run the Flask development server on port 8080
app.run(host='0.0.0.0', port=port, debug=True)

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8080)