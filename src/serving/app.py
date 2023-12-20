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
dataset = '../data/all_new_game_data_with_features.csv'
app = Flask(__name__)
# api = API(os.environ.get('COMET_API_KEY'))
api = API('h85xbEnyF7lyFkSRYhBshWV8E')
path = f'../data/{dataset}'
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




@app.route('/predict', methods=['POST'])
def predict():

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
    file = open('flask.log', 'r')
    response = file.read().splitlines()
    file.close()
    
    return jsonify(response) 

@app.route('/download_registry_model', methods=['POST'])
def download_registry_model():
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

    respond = 'SUCCESS: '+ model_name + ' is loaded!'
    app.logger.info(respond)
    return jsonify(respond) 


def clean_log_file():
    open('flask.log', 'w').close()

# Set the port to 8080
port = 8080

# clean the log file
clean_log_file()

# Run the Flask development server on port 8080
app.run(port=port, debug=True)