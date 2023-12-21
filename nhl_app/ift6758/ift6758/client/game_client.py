import requests
import pandas as pd
import logging

from nhl_tidy_data_new_api import convert_single_play_data
from src.feature_engineering import FeatureEngineering
from serving_client import ServingClient
logger = logging.getLogger(__name__)
serving_client = ServingClient(ip="127.0.0.1", port=8080)

class GameClient:
    def __init__(self):
        self.processed_events = {}  # Dictionary to keep track of processed events by game_id

    def fetch_live_game_data(self, game_id):
        """
                Fetches live game data for a given game_id from the NHL API. Returns
                the game data as a JSON object if successful, or None if the request fails.

                Args:
                    game_id (str): The game ID for which live data is to be fetched.

                Returns:
                    dict or None: The live game data as a JSON object, or None if the request fails.
        """
        url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def ping_game(self, game_id, serving_client):
        """
                Processes new events for a given game_id. It fetches live game data,
                extracts new events, processes them to extract features, gets predictions
                using the serving client, and updates the processed events tracker.

                Args:
                    game_id (str): The game ID for which new events are to be processed.
                Returns:
                    DataFrame or None: A DataFrame containing predictions for new events,
                    or None if there are no new events.
        """
        new_events = []
        game_data = self.fetch_live_game_data(game_id)

        # Check if the game is live or has ended
        live = game_data.get('gameState') != 'OFF'

        # Extract current play details
        period = game_data.get('period', 0)
        timeLeft = game_data['clock']['timeRemaining']
        home_score = game_data['homeTeam']['score']
        away_score = game_data['awayTeam']['score']

        for play in game_data['plays']:
            event_id = play.get('eventId')
            if event_id and event_id not in self.processed_events.get(game_id, set()):
                new_events.append(play)

        if new_events:
            # Create a temporary structure with only new events
            temp_game_data = game_data.copy()
            temp_game_data['plays'] = new_events
            # print(temp_game_data)
            df = self.extract_features(temp_game_data)  # passing the entire structure

            predictions = serving_client.predict(df)
            self.update_processed_events(game_id, new_events)

        return {
            "predictions": predictions,
            "live": live,
            "period": period,
            "timeLeft": timeLeft,
            "home_score": home_score,
            "away_score": away_score
        }



    def extract_features(self, events):
        """
                Extracts features from raw event data. This function converts the raw
                event data into a format suitable for feature engineering and applies
                feature engineering transformations.

                Args:
                    events (dict): The raw event data.

                Returns:
                    DataFrame: A DataFrame containing the extracted features.
        """
        # feature extraction from events
        df = convert_single_play_data(events)

        # Apply feature engineering
        feat_eng = FeatureEngineering(df)
        feat_eng.tranform()
        df = feat_eng.df
        return df

    def update_processed_events(self, game_id, events):
        """
                Updates the internal tracker with processed event IDs for a specific game_id.
                This ensures that these events are not reprocessed in subsequent calls.

                Args:
                    game_id (str): The game ID for which events are to be updated.
                    events (list): A list of event dictionaries that have been processed.
        """
        if game_id not in self.processed_events:
            self.processed_events[game_id] = set()
        for event in events:
            event_id = event.get('eventId')  # Update to use the correct key for event ID
            if event_id:
                self.processed_events[game_id].add(event_id)



#testing
game_client = GameClient()
test_game_id = '2022030411'  # Replace with your test game ID
output = game_client.ping_game(test_game_id, serving_client)
print(output)