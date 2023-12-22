import streamlit as st
import pandas as pd
import requests
from ift6758.ift6758.client import serving_client, game_client
import pandas as pd
import numpy as np

# Initialize session state for temp if not already done
if 'last_game_id' not in st.session_state:
    st.session_state.last_game_id = None
if 'last_selected_model' not in st.session_state:
    st.session_state.last_selected_model = None
if 'game_client' not in st.session_state:
    st.session_state.game_client = game_client.GameClient()
if 'serving_client' not in st.session_state:
    st.session_state.serving_client = serving_client.ServingClient(ip='serving', port=8080)


#=== Title
st.title("NHL Game Analysis Dashboard")
st.subheader('Current Live Games')

with st.sidebar:
    workspace = st.selectbox("Workspace", ["mahmoodhegazy"])
    model = st.selectbox("Model", ["log", "logdist"])
    version = st.selectbox("Version", ["1.0.0"])
    if st.button('Get Model'):
        # Download model from CometML
        st.session_state.serving_client.download_registry_model(workspace, model, version)
        st.success('Model Downloaded')
        # Monitor changes in the selected model
        if model != st.session_state.last_selected_model:
            st.session_state.temp = 0
            st.session_state.last_game_id = None
            st.session_state.last_selected_model = model


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

        st.subheader("Data used for predictions (and predictions)")
        # Update the last pinged game ID and temp
        st.session_state.last_game_id = game_id

        if st.session_state.game_data.get('df') is not None and not st.session_state.game_data['df'].empty:
            st.dataframe(st.session_state.game_data['df'])
        else:
            st.write("No new data available for this game.")

      else:
        st.warning("Please enter a Game ID before pinging.")



# Display the dataframe from session state