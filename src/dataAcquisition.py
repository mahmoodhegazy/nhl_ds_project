import os
import json
import requests as rest
from itertools import product
from tqdm import tqdm



class DataAcquisition():

    def __init__(self):
        # specifying endpoints as vars for future proofing
        self.game_endpoint = "https://statsapi.web.nhl.com/api/v1/game"
        self.schedule_endpoint = "https://statsapi.web.nhl.com/api/v1/schedule"

    def _get_game_request_url(self, game_id:str) -> str:
        """
        Args: 
            game_id: str

        Return: Rest endpoint for that game_id
        """
        return f'{self.game_endpoint}/{game_id}/feed/live/'
    
    def _get_season_games_request_url(self, season:str) -> str:
        """
        Args: 
            season: str

        Return: Rest endpoint for that season
        """
        return f'{self.schedule_endpoint}?season={season}'
    
    def _get_associated_game_ids(self, game_type: str, season: str) -> list:
        """
        Args: 
            game_type: specified game type
            season: specified season
        Returns:
        list of game IDs from the NHL API for a specified game_type/season
        
        """

        # Make a GET request to the NHL API
        response = rest.get(self._get_season_games_request_url(season))

        # Check if the request was successful
        # If not we will handle by returning empty list
        if response.status_code != 200:
            return []

        # Parse the JSON response
        data = response.json()

        game_ids = []
        # Iterate through all games and if game
        # game found to be of specified game type, append to game_ids
        for date in data.get('dates', []):
            for game in date.get('games', []):
                curr_game_id = game.get('gamePk', 0)
                curr_game_type = game.get('gameType', '')
                if curr_game_type == game_type:
                    game_ids.append(str(curr_game_id))

        return game_ids

        
    def get_game_data(self, game_id:str) -> dict:
        """
        Args:
            game_id: str to indentify game to get
        This function will call the api to get data for a specific game
        Returns None if the request was not successful
        """
        '''

        To download a specific game and save the JSON in the given `filepath`.
        Game ID is extracted from the `filepath`. Returns the extracted JSON.
        returns: dict 
        '''
        # GET request to the API for specified game
        response = rest.get(self._get_game_request_url(game_id))
        game_data = None
        if response.status_code == 200:
            game_data = response.json()

        return game_data 


    def _save_game_data(self, game_data:dict, filepath:str):
        """
        Args:
            game_data: dict of game data to save
            filepath: where to save the data
        Helper method to save endpoint data for specific game to filepath
        """
        if game_data:
            with open(filepath, "w") as out_path:
                json.dump(game_data, out_path, indent=4)
       

    def _get_filepath_for_game(self, parent_dir:str, season:str, game_type:str, game_id:str):
        '''
        Args:
            parent_dir: directory at which data will be stored
            season: str of format YYYYYYYY for ex. 20172018 (as required by api)
            game_type: either R for regular or P for playoffs
            game_id: str 
        Returns:
            The filepath given the season, game_type and game_id
        '''
        # Get directory path without the filename
        dir_path = os.path.join(parent_dir, season, game_type.upper())
        # Create the directory if it doesn't exist
        os.makedirs(dir_path, exist_ok=True)
        # Return the complete filepath with the '.json' extension
        return os.path.join(dir_path, f'{game_id}.json')

    
    def download_play_by_play_data_for_season(self, season: str, game_type:str):
        """
        Args:
            season: str of format YYYYYYYY for ex. 20172018 (as required by api)
            game_type: either R for regular or P for playoffs
        Return:
            downloads all play by play data for specific season (either Playoffs or Regular)
        """
        # assertions to make sure call was correct
        assert game_type in ["R","P"]
        assert len(season) == 8

        game_ids = self._get_associated_game_ids(game_type=game_type, season=season)
        for game_id in game_ids:
            game_data = self.get_game_data(game_id=game_id)
            self._save_game_data(game_data=game_data, filepath=self._get_filepath_for_game(parent_dir="data",season=season,game_type=game_type,game_id=game_id))

    def download_all_play_by_play_data(self, seasons:list, game_types:list):
        """
        Args:
            seasons: list of season str of format YYYYYYYY for ex. 20172018 (as required by api)
            game_types: list if game_types (either R for regular or P for playoffs)
        Return:
            downloads all play by play data for specified season and gametype combos
        """
        # To loop through both lists effeciently we can use itertools product
        season_gt_combs = product(seasons, game_types)
        for season, game_type in tqdm(season_gt_combs, desc="Processing"):
            self.download_play_by_play_data_for_season(season=season,game_type=game_type)



