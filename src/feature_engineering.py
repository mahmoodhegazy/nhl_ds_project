import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import seaborn as sns


class FeatureEngineering():

    def __init__(self, path_to_tidy_data='data/all_game_data.csv'):
        """
        This class is the main class for feature Engineering, it is where the feature eng for milestone 2 lies

        Args:
        path_to_tiny_data: path to tidy data devoloped in milestone 1
        """
        
        self.df = pd.read_csv(path_to_tidy_data)
    
    def tranform(self):
        """
        Helper method for all Feature Engineering 1 transformations in milestone 2
        """
        ## Defined Transforms
        self.df['distance_to_positive_goal'] = np.sqrt((self.df['x_coordinate'] - 84)**2 + self.df['y_coordinate']**2)
        self.df['distance_to_negative_goal'] = np.sqrt((self.df['x_coordinate'] + 84)**2 + self.df['y_coordinate']**2)
        self.df['goal_coordinate'] = np.where(self.df['distance_to_positive_goal'] < self.df['distance_to_negative_goal'], 84, -84)
        self.df['shot_distance_to_goal'] = self.df[['distance_to_positive_goal', 'distance_to_negative_goal']].min(axis=1)

        # Get Angle
        # Ensure shot_distance_to_goal is not zero to avoid division by zero
        self.df['shot_distance_to_goal'] = np.where(self.df['shot_distance_to_goal'] == 0, np.nan, self.df['shot_distance_to_goal'])
        # Calculate the ratio and ensure it's within [-1, 1] to avoid invalid values for arcsin
        ratio = self.df['y_coordinate'] / self.df['shot_distance_to_goal']
        ratio = np.clip(ratio, -1, 1)
        # Calculate the angle
        self.df['angle'] = np.where(self.df['goal_coordinate'] == 84, 
                       np.arcsin(ratio) * 180 / math.pi, 
                       np.arcsin(ratio) * -180 / math.pi)
        self.df['angle'].fillna(0, inplace=True)
        self.df['shot_distance_to_goal'].fillna(0, inplace=True)

        self.df['is_goal'] = self.df['is_goal'].fillna(0).astype(int)
        self.df['is_emptyNet'] = self.df['is_emptyNet'].fillna(0).astype(int)
        

        goal_rate = self.df['is_goal'].sum() / len(self.df)
        self.df['goal_rate_dist'] = goal_rate / self.df['shot_distance_to_goal']  
        self.df['goal_rate_angle'] = goal_rate / self.df['angle']
        self.df['goal_rate_dist'] = self.df['goal_rate_dist'].replace([math.inf], 1)
        self.df['goal_rate_angle'] = self.df['goal_rate_angle'].replace([-math.inf], 1)
        self.df['goal_rate_angle'] = self.df['goal_rate_angle'].replace([math.inf], 1)
    
    def train_test_split(self, seasons_train=["20162017", "20172018", "20182019"], season_test="20192020"):
        df_train = self.df[self.df['season'].isin(seasons_train)]
        df_test = self.df[self.df['season'] == season_test]
        return df_train, df_test


    


    

