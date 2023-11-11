import json
import pandas as pd
import numpy as np
import os

"""Create a function to convert all events of every game into a pandas dataframe.

For this milestone, you will want to include events of the type “shots” and “goals”. You can ignore missed shots or blocked shots for now. For each event, you will want to include as features (at minimum): game time/period information, game ID, team information (which team took the shot), indicator if its a shot or a goal, the on-ice coordinates, the shooter and goalie name (don’t worry about assists for now), shot type, if it was on an empty net, and whether or not a goal was at even strength, shorthanded, or on the power play.

"""

def tidy_one_game_data(raw_data: dict):
    # Early exit if 'liveData' is not present
    if 'liveData' not in raw_data:
        return None

    # Initialize DataFrame
    columns = ['gameID', 'eventID', 'gameID_eventID', 'game_period', 'game_time', 'team', 'goal', 'x', 'y', 'shooter', 'goalie', 'shotType', 'emptyNet', 'strength', 'gameType', 'home', 'away', 'season', 'game_seconds', 'last_event', 'last_x_coordinate', 'last_y_coordinate', 'time_from_last_event', 'distance_from_last_event', 'rebound', 'speed', 'power_play_time','time_since_powerplay_started'] #, 'nbFriendly_non_goalie_skaters', 'nbOpposing_non_goalie_skaters']
    # df = pd.DataFrame(columns=columns)
    single_play_data_list = []

    # Extracting basic game info
    game_info = raw_data['gameData']['game']
    gameID, gameType, season = raw_data['gamePk'], game_info['type'], game_info['season']
    teams_info = raw_data['gameData']['teams']
    home, away = teams_info['home']['name'], teams_info['away']['name']

    # Initialize variables for penalty tracking
    penalties = {'team1': {'minor': [], 'doubleMinor': [], 'major': [], 'reserved': [], 'nbPlayerDown': 0},
                 'team2': {'minor': [], 'doubleMinor': [], 'major': [], 'reserved': [], 'nbPlayerDown': 0}}
    team_names = {home: 'team1', away: 'team2'}
    power_play_time = 0

    for index, play in enumerate(raw_data['liveData']['plays']['allPlays']):
        # Process each play
        about, result = play['about'], play['result']
        period, period_time = about['period'], about['periodTime']
        gamePlayTime = (period - 1) * 20 * 60 + int(period_time[:2]) * 60 + int(period_time[3:])

        # Update penalties and power play status
        update_penalties(penalties, gamePlayTime)
        power_play_time = update_power_play(penalties, power_play_time, gamePlayTime)

        # Process 'Shot' or 'Goal' plays
        if result['event'] in ['Shot', 'Goal']:
            play_data = process_play(play, gameID, home, away, penalties, team_names, gamePlayTime, power_play_time, index, raw_data)
            single_play_data_list.append(play_data)
        elif result['event'] == 'Penalty': # Check if the current play is a penalty and update penalties accordingly (BONUS) play['about']['eventIdx'] in raw_data['liveData']['plays']['penaltyPlays'] and 
            penalty_minutes = play['result']['penaltyMinutes']
            penaltyTime = gamePlayTime + penalty_minutes * 60
            team_key = team_names[play['team']['name']]

            # Add penalty based on the minutes
            if penalty_minutes < 4:
                penalty_type = 'minor'
            elif penalty_minutes == 4:
                penalty_type = 'doubleMinor'
            else:
                penalty_type = 'major'

            if penalties[team_key]['nbPlayerDown'] < 2:
                penalties[team_key][penalty_type].insert(0, penaltyTime)
                penalties[team_key]['nbPlayerDown'] += 1
            else:
                reserved_code = {'minor': 0, 'doubleMinor': 1, 'major': 2}[penalty_type]
                penalties[team_key]['reserved'].insert(0, reserved_code)

    # Drop rows with missing coordinates and return DataFrame
    # df.dropna(axis=0, subset=['x', 'y'], inplace=True)
    return pd.DataFrame(single_play_data_list)

def update_penalties(penalties, gamePlayTime):
    """
    This function updates the penalty status for each team. The logic involves removing finished penalties and serving reserved penalties.
    """
    for team in ['team1', 'team2']:
        for penalty_type in ['minor', 'doubleMinor', 'major']:
            # Remove finished penalties
            while penalties[team][penalty_type] and penalties[team][penalty_type][-1] <= gamePlayTime:
                penalties[team][penalty_type].pop()
                if penalty_type != 'doubleMinor':
                    penalties[team]['nbPlayerDown'] -= 1
                elif len(penalties[team]['doubleMinor']) % 2 == 0:
                    penalties[team]['nbPlayerDown'] -= 1

            # Serve reserved penalties
            while penalties[team]['reserved'] and penalties[team]['nbPlayerDown'] < 2:
                r = penalties[team]['reserved'].pop()
                penalty_duration = [2 * 60, 4 * 60, 5 * 60][r]  # Minor, Double Minor, Major
                for _ in range(1 if r != 1 else 2):  # Double minor adds two penalties
                    penalties[team][penalty_type].insert(0, gamePlayTime + penalty_duration)
                    penalties[team]['nbPlayerDown'] += 1

def update_power_play(penalties, power_play_time, game_play_time):
    """
    This function updates the power play status. It sets or resets the power_play_time based on the number of players down on each team.
    """
    if penalties['team1']['nbPlayerDown'] != penalties['team2']['nbPlayerDown'] and power_play_time == 0:
        power_play_time = game_play_time  # Start power play
    elif penalties['team1']['nbPlayerDown'] == penalties['team2']['nbPlayerDown'] and power_play_time != 0:
        power_play_time = 0  # Reset power play
    
    return power_play_time


def process_play(single_play, game_id, home, away, penalties, team_names, game_play_time, power_play_time, index, raw_data):

    event_type =  single_play['result']['event']
    team_playing = team_names[single_play['team']['name']]
    opposing_team = 'team2' if team_playing == 'team1' else 'team1'
    # about = single_play['about']
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

    # get the game evet id/time/period information
    event_id = single_play['about']['eventId']
    event_data["eventID"] = event_id
    event_data["gameID_eventID"] = f"{game_id}_{event_id}"
    event_data['game_time'] = single_play['about']['dateTime']
    event_data['game_period'] = single_play['about']['period']
    event_data['team'] = single_play['team']['name']

    # get the on-ice coordinates
    event_data['x_coordinate'] = single_play['coordinates'].get('x', None)
    event_data['y_coordinate'] = single_play['coordinates'].get('y', None)

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

        #releasing penalized players during a power-play when a goal is scored
        if penalties[team_playing]['nbPlayerDown'] != penalties[opposing_team]['nbPlayerDown']:
            release_penalized_players(penalties[opposing_team])

  
    # Additional processing common to both shots and goals
    # Game Seconds
    period_time = single_play['about']['periodTime']
    period = single_play['about']['period']
    event_data["game_seconds"] = (period-1)*20+(int(period_time.split(':')[0])*60)+int(period_time.split(':')[1])

    # Last event type
    event_data["time_from_last_event"] = None
    event_data["last_x_coordinate"] = None
    event_data["last_y_coordinate"] = None
    event_data["last_event"] = None

    if (index > 0) & (index<len(raw_data['liveData']['plays']['allPlays'])):
        previous_play = raw_data['liveData']['plays']['allPlays'][index - 1]
        event_data["last_event"] = previous_play['result']['event']
        # Coordinates of the last event (x, y)
        event_data["last_x_coordinate"] = previous_play['coordinates'].get('x', None)
        event_data["last_y_coordinate"] = previous_play['coordinates'].get('y', None)
        #Time from the last event (seconds)
        last_period_time = previous_play['about']['periodTime']
        last_period = previous_play['about']['period']
        previous_game_seconds = (last_period-1)*20+(int(last_period_time.split(':')[0])*60)+int(last_period_time.split(':')[1])
        event_data["time_from_last_event"] = event_data["game_seconds"] - previous_game_seconds
    
    # Calculate Distance from the last event
    if all(v is not None for v in [event_data["x_coordinate"], event_data["y_coordinate"], event_data["last_x_coordinate"], event_data["last_y_coordinate"]]):
        event_data["distance_from_last_event"] = np.linalg.norm(np.array([event_data["x_coordinate"], event_data["y_coordinate"]]) - np.array([event_data["last_x_coordinate"],event_data["last_y_coordinate"]]))      
    else:
        event_data["distance_from_last_event"] = None    
    
    # Rebound
    event_data["rebound"] = True if (event_data["last_event"] is not None and event_data["last_event"] == 'Shot' and event_type =='Shot') else False

    # Speed 
    if all(v is not None for v in [event_data["distance_from_last_event"], event_data["time_from_last_event"]]) and event_data["time_from_last_event"]!=0:
        event_data["speed"] = event_data["distance_from_last_event"]/event_data["time_from_last_event"]
    else:
        event_data["speed"] = None
        
    # Time elapsed since start of power-play
    event_data["power_play_time"] = power_play_time
    event_data["time_since_powerplay_started"] = game_play_time - power_play_time if power_play_time != 0 else 0

    # Calculate the number of skaters for each team
    friendly_non_goalie_skaters = 5 - penalties[team_playing]['nbPlayerDown']
    opposing_non_goalie_skaters = 5 - penalties[opposing_team]['nbPlayerDown']
    # Ensure that the number of skaters does not go below 3 as a team must have at least three skaters on the ice at all times in hockey
    event_data['num_friendly_non_goalie_skaters'] = max(friendly_non_goalie_skaters, 3)
    event_data['num_opposing_non_goalie_skaters'] = max(opposing_non_goalie_skaters, 3)
    
    # Return a dictionary with all the necessary data
    return event_data


def release_penalized_players(penalty_info):
    # Release the players from the minor or double minor penalties
    if penalty_info['minor']:
        penalty_info['minor'].pop()
        penalty_info['nbPlayerDown'] -= 1
    elif penalty_info['doubleMinor']:
        penalty_info['doubleMinor'].pop()
        if len(penalty_info['doubleMinor']) % 2 == 0:
            penalty_info['nbPlayerDown'] -= 1


def process_game_json(file_path):
    with open(file_path, 'r') as file:
        raw_data = json.load(file)
    return tidy_one_game_data(raw_data)

def concatenate_all_games_data(dataset_root_dir):
    all_games_data = []

    for root, dirs, files in os.walk(dataset_root_dir):
        print(f'Processing directory: {root}')  # Debugging information
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                # print('Processing file: {file_path}')
                game_data_df = process_game_json(file_path)
                all_games_data.append(game_data_df)

    # Concatenate all individual game data DataFrames into a single DataFrame
    all_games_df = pd.concat(all_games_data, ignore_index=True)

    return all_games_df


# Usage:
# dataset_root_dir = 'Data'
# all_games_df = concatenate_all_games_data(dataset_root_dir)
# # generate a csv file
# all_games_df.to_csv('data/all_game_data.csv', index=False)