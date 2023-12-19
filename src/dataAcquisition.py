import os
import json
import requests as rest
from itertools import product
from tqdm import tqdm



class DataAcquisition():

    def __init__(self, seasons, game_types, files_path="data"):
        # specifying endpoints as vars for future proofing
        self.game_endpoint = "https://api-web.nhle.com/v1/gamecenter"
        self.schedule_endpoint = "https://api-web.nhle.com/v1/club-schedule-season"
        self.teams_endpoint = "https://api.nhle.com/stats/rest/en/team"
        self.seasons = seasons
        self.game_types = game_types
        self.files_path = files_path

    def _get_game_request_url(self, game_id:str) -> str:
        """
        Args: 
            game_id: str

        Return: Rest endpoint for that game_id
        """
        return f'{self.game_endpoint}/{game_id}/play-by-play'
    
    def _get_season_games_request_url(self, season:str, team:str) -> str:
        """
        Args: 
            season: str

        Return: Rest endpoint for that season
        """
        return f'{self.schedule_endpoint}/{team}/{season}'
    
    def _get_associated_teams(self) -> list:
        """
        Args: 
        Returns:
        list of team IDs from the NHL API, needed to get all game_ids

        """

        # Make a GET request to the NHL API
        response = rest.get(self.teams_endpoint)

        # Check if the request was successful
        # If not we will handle by returning empty list
        if response.status_code != 200:
            return []

        # Parse the JSON response
        data = response.json()

        teams = []
        # Iterate through all teams and get code
        for team in data.get('data', []):
            teams.append(team.get('triCode', []))

        return teams
    



    def get_associated_game_ids(self, seasons: list, game_types: list) -> list:
        """
        Args: 
            game_types: specified game types
            seasons: specified seasons
        Returns:
        list of game IDs from the NHL API for a specified game_type/season
        
        """

        # Iterate through all games and if game
        # game found to be of specified game types, append to game_ids
        game_ids = []
        self.teams = self._get_associated_teams()

        for team in self.teams:
            for season in  seasons:
                # Make a GET request to the NHL API
                response = rest.get(self._get_season_games_request_url(season=season, team=team))
                if response.status_code != 200: #if response was not successful skip this combo
                    continue
                data = response.json() # Parse the JSON response
                season_games = data.get('games',[]) # Get season games
                for game in season_games:
                    curr_game_id = game.get("id", 0)
                    curr_game_type = game.get("gameType", '')
                    if str(curr_game_type) in game_types:
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
       

    def _get_filepath_for_game(self, parent_dir:str, game_id:str):
        '''
        Args:
            parent_dir: directory at which data will be stored speicified by user
            game_id: str 
        Returns:
            The filepath given game_id
        '''
        # Get directory path without the filename
        dir_path = os.path.join(parent_dir)
        # Create the directory if it doesn't exist
        os.makedirs(dir_path, exist_ok=True)
        # Return the complete filepath with the '.json' extension
        return os.path.join(dir_path, f'{game_id}.json')

    
    def download_play_by_play_data_for_specific_season_gametype(self, season: str, game_type:str):
        """
        Args:
            season: str of format YYYYYYYY for ex. 20172018 (as required by api)
            game_type: either R for regular or P for playoffs
        Return:
            downloads all play by play data for specific season (either Playoffs or Regular)
        """
        # assertions to make sure call was correct
        assert len(season) == 8
        assert game_type in ["2","3"]

        game_ids = self.get_associated_game_ids(game_types=[game_type], seasons=[season])
        for game_id in tqdm(game_ids, desc="Processing"):
            game_data = self.get_game_data(game_id=game_id)
            self._save_game_data(game_data=game_data, filepath=self._get_filepath_for_game(parent_dir=self.files_path, game_id=game_id))


    def download_all_play_by_play_data(self):
        """
        Args:
        Return:
            downloads all play by play data for specified seasons and gametypes
        """

        game_ids = self.get_associated_game_ids(game_types=self.game_types, seasons=self.seasons)
        for game_id in tqdm(game_ids, desc="Processing"):
            game_data = self.get_game_data(game_id=game_id)
            self._save_game_data(game_data=game_data, filepath=self._get_filepath_for_game(parent_dir=self.files_path, game_id=game_id))



