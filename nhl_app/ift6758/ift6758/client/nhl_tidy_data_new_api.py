import json
import pandas as pd
import os

"""Create a function to convert all events of every game into a pandas dataframe.

For this third milestone, we will rewrite milestone 1 code to work with th enew api.. 
we want to include events of the type “shots” and “goals”. You can ignore missed shots or blocked shots for now. For each event, you will want to include as features (at minimum): game time/period information, game ID, team information (which team took the shot), indicator if its a shot or a goal, the on-ice coordinates, the shooter and goalie name (don’t worry about assists for now), shot type, if it was on an empty net, and whether or not a goal was at even strength, shorthanded, or on the power play.

"""

def convert_single_play_data(raw_data):
    single_play_data_list = []

    # print(season)
    for single_play in raw_data['plays']:
      event_type =  single_play['typeDescKey']
      event_code =  single_play['typeCode']
      home_team_id = raw_data['homeTeam']['id']
      away_team_id = raw_data['awayTeam']['id']
      event_data = {
          'event_type': event_type,
          'gameID': raw_data['id'],
          'gameType': raw_data['gameType'],
          'home': raw_data['homeTeam']['name']['default'],
          'home_id': home_team_id,
          'away': raw_data['awayTeam']['name']['default'],
          'away_id': away_team_id,
          'season': raw_data['season']
      }
      # if "shot" in event_type or event_type == "goal":
      if event_code in [505, 506, 507, 508]: #goals and shots codes according to https://gitlab.com/dword4/nhlapi/-/issues/110
        # get the game time/period information
        event_data['game_period'] = single_play['period']
        event_data['time_remaining_in_period'] = single_play['timeRemaining']
        # get the on-ice coordinates
        event_data['x_coordinate'] = single_play['details'].get('xCoord', None)
        event_data['y_coordinate'] = single_play['details'].get('yCoord', None)

        # get the shot type
        event_data['shot_type'] = single_play['details'].get('shotType',None)

        event_data['shooter_id'] = single_play['details'].get('scoringPlayerId', None)
        event_data['goalie_id'] = single_play['details'].get('goalieInNetId', None)
        event_data['event_team'] = "home" if single_play['details'].get("eventOwnerTeamId", None) == home_team_id else "away"

        if event_type == 'goal':
          event_data['is_goal'] = True
          event_data['scoring_team'] = "home" if single_play['details'].get("eventOwnerTeamId", None) == home_team_id else "away"
          # Get if goal was empty, 
          # if home team scoring we check if away goalie was on ice using 1st digit in situation code (if digit is 1 then not an empty net)
          # if away team scoring we check if home goalie was on ice using 4th digit in situation code (if digit is 1 then not an empty net)
          event_data['is_emptyNet'] = not int(single_play['situationCode'][0]) if event_data['scoring_team'] == "home" else not int(single_play['situationCode'][3]) 
        else:
          event_data['is_goal'] = False

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

# # Usage:
# dataset_root_dir = 'new_data'
# all_games_df = concatenate_all_games_data(dataset_root_dir)
# # generate a csv file
# all_games_df.to_csv('data/all_new_game_data.csv', index=False)