import requests
import pandas as pd
import logging

from .nhl_tidy_data_new_api import convert_single_play_data
from .feature_engineering import FeatureEngineering
from .serving_client import ServingClient
logger = logging.getLogger(__name__)
serving_client = ServingClient(ip="127.0.0.1", port=8080)

class GameClient:
    def __init__(self, game_id = 2022030411, xg_home = 0, xg_away = 0, last_idx = 0):
        self.game_tracker = {game_id:(xg_home, xg_away, last_idx)} # Dictionary to keep track of game_id progress

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

    def ping_game(self, game_id):
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
        xg_home, xg_away, last_idx = 0,0,0

        # Check if game_id stored, if, yes get where we left off, if not add it to dict
        if game_id in self.game_tracker:
            xg_home, xg_away, last_idx = self.game_tracker[game_id]
        else:
            self.game_tracker[game_id] = 0,0,0

        # Check if the game is live or has ended
        live = game_data.get('gameState') != 'OFF'

        # Extract current play details
        period = game_data.get('period', 0)
        timeLeft = game_data['clock']['timeRemaining']
        home_name = game_data['homeTeam']['name']['default']
        away_name = game_data['awayTeam']['name']['default']
        home_score = game_data['homeTeam']['score']
        away_score = game_data['awayTeam']['score']

        # Only predict events that have not been considered yet
        if len(game_data['plays']) == last_idx:
            new_events = None
        else:
            new_events.extend(game_data['plays'][last_idx:])

        # Init predicitons 
        df_with_predictions = pd.DataFrame()

        if new_events:
            # Create a temporary df with only new events
            temp_game_data = game_data.copy()
            temp_game_data['plays'] = new_events
            df = self.extract_features(temp_game_data)
            # Seperate home events from away events
            df_home = df[df.event_team == "home"][["shot_distance_to_goal", "shot_angle"]]
            df_away = df[df.event_team == "away"][["shot_distance_to_goal", "shot_angle"]]
            # Get preds for home and away
            preds_home = serving_client.predict(df_home)
            preds_away = serving_client.predict(df_away)
            df_home["team"] = "home"
            df_home["xG"] = preds_home["xG"].tolist()
            df_away["team"] = "away"
            df_away["xG"] = preds_away["xG"].tolist()
            # Concat to return data to show 
            df_with_predictions = pd.concat([df_home, df_away])
            # Calculate new xg_home and xg_away
            xg_home += preds_home["xG"].sum()
            xg_away += preds_away["xG"].sum()
        
        last_idx = len(game_data['plays']) #update last_idx
        self.game_tracker[game_id] = xg_home, xg_away, last_idx

        return {
            "df": df_with_predictions,
            "live": live,
            "period": period,
            "timeLeft": timeLeft,
            "home_name": home_name,
            "away_name": away_name,
            "home_score": home_score,
            "away_score": away_score,
            "home_xG": xg_home,
            "away_xG": xg_away,
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
