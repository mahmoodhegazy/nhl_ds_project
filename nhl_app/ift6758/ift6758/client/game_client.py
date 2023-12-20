import requests
import pandas as pd
import logging

from src.nhl_tidy_data_new_api import convert_single_play_data
from src.feature_engineering import FeatureEngineering
from serving_client import ServingClient
logger = logging.getLogger(__name__)
serving_client = ServingClient()

class GameClient:
    def __init__(self):
        self.processed_events = {}  # Dictionary to keep track of processed events by game_id

    def fetch_live_game_data(self, game_id):
        url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def process_new_events(self, game_id, serving_client):
        new_events = []
        game_data = self.fetch_live_game_data(game_id)

        for play in game_data['plays']:
            event_id = play.get('eventId')
            if event_id and event_id not in self.processed_events.get(game_id, set()):
                new_events.append(play)

        if new_events:
            # Create a temporary structure with only new events
            temp_game_data = game_data.copy()
            temp_game_data['plays'] = new_events
            print(temp_game_data)
            df = self.extract_features(temp_game_data)  #passing the entire structure
            predictions = serving_client.predict(df)
            self.update_processed_events(game_id, new_events)
            return predictions

        return None



    def extract_features(self, events):
        # feature extraction from events
        df = convert_single_play_data(events)

        # Apply feature engineering
        feat_eng = FeatureEngineering(df)
        transformed_df = feat_eng.tranform()
        return transformed_df

    def update_processed_events(self, game_id, events):
        if game_id not in self.processed_events:
            self.processed_events[game_id] = set()
        for event in events:
            event_id = event.get('eventId')  # Update to use the correct key for event ID
            if event_id:
                self.processed_events[game_id].add(event_id)

