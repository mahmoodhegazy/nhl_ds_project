import json
import pandas as pd
import os

"""Create a function to convert all events of every game into a pandas dataframe.

For this milestone, you will want to include events of the type “shots” and “goals”. You can ignore missed shots or blocked shots for now. For each event, you will want to include as features (at minimum): game time/period information, game ID, team information (which team took the shot), indicator if its a shot or a goal, the on-ice coordinates, the shooter and goalie name (don’t worry about assists for now), shot type, if it was on an empty net, and whether or not a goal was at even strength, shorthanded, or on the power play.

"""

def convert_single_play_data(raw_data):
    single_play_data_list = []

    # print(season)
    for single_play in raw_data['liveData']['plays']['allPlays']:
      event_type =  single_play['result']['event']
      event_data = {
          'event_type': event_type,
          # get the game ID
          'gameID': raw_data['gamePk'],
          # print(gameID)
          'gameType': raw_data['gameData']['game']['type'],
          # print(gameType)
          'home': raw_data['gameData']['teams']['home']['name'],
          # print(home)
          'away': raw_data['gameData']['teams']['away']['name'],
          # print(away)
          'season': raw_data['gameData']['game']['season']
      }
      if event_type in ['Shot', 'Goal']:
        # get the game time/period information
        event_data['game_time'] = single_play['about']['dateTime']
        event_data['game_period'] = single_play['about']['period']
        event_data['team'] = single_play['team']['name']

        # get the on-ice coordinates
        event_data['x_coordinate'] = single_play['coordinates'].get('x', None),
        event_data['y_coordinate'] = single_play['coordinates'].get('y', None),

        # get the short type
        event_data['shot_type'] = single_play['result'].get('secondaryType',None)

        if event_type == 'Shot':
          event_data['is_goal'] = False
          # Extracting shooter and goalie names
          for player in single_play['players']:
            if player['playerType'] == 'Shooter':
              event_data['shooter'] = player['player']['fullName']
            elif player['playerType'] == 'Goalie':
              event_data['goalie'] = player['player']['fullName']

        elif event_type == 'Goal':
          event_data['is_goal'] = True
          for player in single_play['players']:
              if player['playerType'] == 'Scorer':
                event_data['shooter'] = player['player']['fullName']
              if player['playerType'] == 'Goalie':
                event_data['goalie'] = player['player']['fullName']
          event_data['is_emptyNet'] = single_play['result'].get('emptyNet', None)
          event_data['strength'] = single_play['result'].get('strength',None).get('name', None)

        single_play_data_list.append(event_data)

    # Converting the list of event data into a Pandas DataFrame
    single_play_df = pd.DataFrame(single_play_data_list)
    return single_play_df

def process_game_json(file_path):
    with open(file_path, 'r') as file:
        raw_data = json.load(file)
    return convert_single_play_data(raw_data)

def concatenate_all_games_data(dataset_root_dir):
    all_games_data = []

    for root, dirs, files in os.walk(dataset_root_dir):
        print(f'Processing directory: {root}')  # Debugging information
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                # print(f'Processing file: {file_path}')
                game_data_df = process_game_json(file_path)
                all_games_data.append(game_data_df)

    # Concatenate all individual game data DataFrames into a single DataFrame
    all_games_df = pd.concat(all_games_data, ignore_index=True)

    return all_games_df

# Usage:
dataset_root_dir = 'Data'
all_games_df = concatenate_all_games_data(dataset_root_dir)
# generate a csv file
all_games_df.to_csv('data/all_game_data.csv', index=False)