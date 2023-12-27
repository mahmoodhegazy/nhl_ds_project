import streamlit as st
import pandas as pd
import requests
from ift6758.ift6758.client import serving_client, game_client
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Initialize session state if not already done
if 'last_game_id' not in st.session_state:
    st.session_state.last_game_id = None
if 'last_selected_model' not in st.session_state:
    st.session_state.last_selected_model = None
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = None

# Initialize the game client
if 'game_client' not in st.session_state:
    st.session_state.game_client = game_client.GameClient()
if 'serving_client' not in st.session_state:
    st.session_state.serving_client = serving_client.ServingClient(ip='serving', port=8080)


#=== Title
st.title("NHL Game Analysis Dashboard")
st.subheader('Current Live Games')

with st.sidebar:
    workspace = st.selectbox("Workspace", ["mahmoodhegazy"])
    selected_model = st.selectbox("Model", ["log", "logdist"])
    version = st.selectbox("Version", ["1.0.0"])
    # Monitor changes in the selected model
    if selected_model != st.session_state.last_selected_model:
        st.session_state.last_selected_model = selected_model
        st.session_state.game_client = game_client.GameClient()
        st.session_state.last_game_id = None

    if st.button('Get Model'):
        # Download model from CometML
        st.session_state.serving_client.download_registry_model(workspace, selected_model, version)
        st.success('Model Downloaded')

def plot_home_and_away_shot_types(df, home_name, away_name):
    """
    This function will plot the (part 7 bonus) pinged events shot stats
    Args:
        df (pandas DataFrame): df with "event_type" column
        home_name (str): home team name
        away_nam (str): away team name
    Returns:
    matplotlib figure to be plotted by streamlit
    """
    df_home = df[df.team == "home"]
    df_away = df[df.team == "away"]
    #collect Home stats
    home_missed_shots = len(df_home[df_home["event_type"] == "missed-shot"])
    home_blocked_shots = len(df_home[df_home["event_type"] == "blocked-shot"])
    home_shots_ongoal = len(df_home[df_home["event_type"] == "shot-on-goal"])
    home_goals = len(df_home[df_home["event_type"] == "goal"])
    # collect away stats
    away_missed_shots = len(df_away[df_away["event_type"] == "missed-shot"])
    away_blocked_shots = len(df_away[df_away["event_type"] == "blocked-shot"])
    away_shots_ongoal = len(df_away[df_away["event_type"] == "shot-on-goal"])
    away_goals = len(df_away[df_away["event_type"] == "goal"])

    home_stats = [home_missed_shots, home_blocked_shots, home_shots_ongoal, home_goals]
    away_stats = [away_missed_shots, away_blocked_shots, away_shots_ongoal, away_goals]
    stat_labels = ['Missed Shots', 'Blocked Shots', 'Shots on Goal', 'Goal']
    team_names = [home_name, away_name]

    fig = plot_team_stats(home_stats, away_stats, stat_labels, team_names)
    return fig


def plot_team_stats(home_stats, away_stats, stat_labels, team_names):
    """
    Helper for plot_home_and_away_shot_types
    """
    x = np.arange(len(stat_labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, home_stats, width, label=team_names[0])
    rects2 = ax.bar(x + width/2, away_stats, width, label=team_names[1])

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Shots')
    ax.set_title('Shots by Category and Team')
    ax.set_xticks(x)
    ax.set_xticklabels(stat_labels)
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)

    return fig

with st.container():

    game_id = st.text_input("Enter Game ID (e.g., 2021020329):")
    ping_button = st.button('Ping game')

    if 'last_game_id' not in st.session_state:
        st.session_state.last_game_id = None

    if ping_button:
      if game_id.strip():
        if game_id == st.session_state.last_game_id:
              st.session_state.game_data = st.session_state.game_client.ping_game(game_id)
        else:
              # Fetch new data
              st.session_state.game_data = st.session_state.game_client.ping_game(game_id)

        st.success(f"Latest data fetched for Game ID: {game_id}")
        # st.session_state.game_data = game_client.ping_game(game_id)
        # Display game information
        st.subheader(
            f"Game {game_id}: {st.session_state.game_data['home_name']} vs {st.session_state.game_data['away_name']}")
        st.write(
            f"Period: {st.session_state.game_data['period']} - Time left: {st.session_state.game_data['timeLeft']}")
        # Use columns to display metrics side by side
        col1, col2 = st.columns(2)
        with col1:
            home_xG_formatted = "{:.1f}".format(st.session_state.game_data['home_xG'])
            home_delta = st.session_state.game_data['home_score'] - st.session_state.game_data['home_xG']
            home_delta_formatted = "{:.1f}".format(home_delta)
            st.metric(f"{st.session_state.game_data['home_name']} xGoals (Actual)",
                      f"{home_xG_formatted} ({st.session_state.game_data['home_score']})",
                      delta=home_delta_formatted)

        with col2:
            away_xG_formatted = "{:.1f}".format(st.session_state.game_data['away_xG'])
            away_delta = st.session_state.game_data['away_score'] - st.session_state.game_data['away_xG']
            away_delta_formatted = "{:.1f}".format(away_delta)
            st.metric(f"{st.session_state.game_data['away_name']} xGoals (Actual)",
                      f"{away_xG_formatted} ({st.session_state.game_data['away_score']})",
                      delta=away_delta_formatted)

        st.subheader("Data used for predictions (and xG predictions)")
        # Update the last pinged game ID and temp
        st.session_state.last_game_id = game_id

        if st.session_state.game_data.get('df') is not None and not st.session_state.game_data['df'].empty:
            if st.session_state.last_selected_model == "logdist": #Only show features showed from predicitons for chosen model
                st.dataframe(st.session_state.game_data['df'][["team_name", "shot_distance_to_goal", "xG"]])
            else:
                st.dataframe(st.session_state.game_data['df'][["team_name", "shot_distance_to_goal", "shot_angle", "xG"]])
            # Bonus Part 7: Plot stats of these pinged events
            st.subheader('Teams New (pinged) Shots Statistics')
            st.write("Here we see shot stats per team for the pinged events (intended as the bonus component). Ideally this would be overall and not just new pinged events but that requires some work in game client to keep track of shot history")
            fig = plot_home_and_away_shot_types(st.session_state.game_data['df'], st.session_state.game_data['home_name'],  st.session_state.game_data['away_name'])
            st.pyplot(fig)
        else:
            st.write("No new data available for this game.")

      else:
        st.warning("Please enter a Game ID before pinging.")



# Display the dataframe from session state