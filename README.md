# IFT6758 NHL Project

This project is the IFT 6758 NHL project, with predicting live game xG capabilities through the NHL app. 


<p align="center">
<img src="./figures/nhl_rink.png" alt="NHL Rink is 200ft x 85ft." width="400"/>
<p>

## Installation

To install this package, first setup your Python environment by following the instructions in the [Environment](#environments) section.
Once you've setup your environment, you can install this package by running the following command from the root directory of your repository. 

    pip install -e .

You should see something similar to the following output:

    > pip install -e .
    Obtaining file:///home/USER/project-template
    Installing collected packages: ift6758
    Running setup.py develop for ift6758
    Successfully installed ift6758-0.1.0


## Environments

The first thing you should setup is your isolated Python environment.
You can manage your environments through either Conda or pip.
Both ways are valid, just make sure you understand the method you choose for your system.
It's best if everyone on your team agrees on the same method, or you will have to maintain both environment files!
Instructions are provided for both methods.

**Note**: If you are having trouble rendering interactive plotly figures and you're using the pip + virtualenv method, try using Conda instead.

### Conda 

Conda uses the provided `environment.yml` file.
You can ignore `requirements.txt` if you choose this method.
Make sure you have [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/products/individual) installed on your system.
Once installed, open up your terminal (or Anaconda prompt if you're on Windows).
Install the environment from the specified environment file:

    conda env create --file environment.yml
    conda activate ift6758-conda-env

After you install, register the environment so jupyter can see it:

    python -m ipykernel install --user --name=ift6758-conda-env

You should now be able to launch jupyter and see your conda environment:

    jupyter-lab

If you make updates to your conda `environment.yml`, you can use the update command to update your existing environment rather than creating a new one:

    conda env update --file environment.yml    

You can create a new environment file using the `create` command:

    conda env export > environment.yml

### Pip + Virtualenv

An alternative to Conda is to use pip and virtualenv to manage your environments.
This may play less nicely with Windows, but works fine on Unix devices.
This method makes use of the `requirements.txt` file; you can disregard the `environment.yml` file if you choose this method.

Ensure you have installed the [virtualenv tool](https://virtualenv.pypa.io/en/latest/installation.html) on your system.
Once installed, create a new virtual environment:

    vitualenv ~/ift6758-venv
    source ~/ift6758-venv/bin/activate

Install the packages from a requirements.txt file:

    pip install -r requirements.txt

As before, register the environment so jupyter can see it:

    python -m ipykernel install --user --name=ift6758-venv

You should now be able to launch jupyter and see your conda environment:

    jupyter-lab

If you want to create a new `requirements.txt` file, you can use `pip freeze`:

    pip freeze > requirements.txt


## Milestone 1

[Milestone 1](./Blog-post/_posts/2023-10-02-milestone1.md)

---
layout: post
title:  "IFT 6758 Project: Milestone 1"
subtitle: "Six Subtitle"
date:   2023-10-02
---


## 1. Data Acquisition
<b> NHL Stats API </b><br>

The NHL offers an API that provides access to extensive play by play information for all NHL games, including both regular season and playoff matches. This data is highly detailed. We can utilise this data for analysis of aspects such as individual player performance and team patterns.

To obtain the play by play data, for a game we send a GET request to the following API endpoint;
{% highlight python %}
https://statsapi.web.nhl.com/api/v1/game/ <game_id> /feed/live/
{% endhighlight %}

with game_id representing the ID of the game you want to retrieve data for. All other useful REST endpoints can be found at the unofficial API found here: https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md


<b> Extracting Data for a single Game </b><br>

Since we've identified the correct endpoint of interest using the game_id, we now want a means to extract the data. We can utilise the Python requests API (https://pypi.org/project/requests/) using the follwing code snippit:

{% highlight python %}
requests.get('https://statsapi.web.nhl.com/api/v1/game/'+str(game_id)+'/feed/live/')
{% endhighlight %}

This will give us a JSON extract of the play-by-play data for that one game.

<b> Extracting Data for Seasons</b><br>

To get all data for specified seasons we need a way of getting all game_ids for a specific season first. To get that we can utilise the NHL API schedule endpoint (https://statsapi.web.nhl.com/api/v1/schedule) to get all game_ids for a specified season. The function we have that does just that that is:

{% highlight python %}
_get_associated_game_ids(self, game_type: str, season: str)
{% endhighlight %}

where game_type can be either 'R' for Regular or 'P' for Playoffs and season is a string of the speicfied season, Ex. "20162017". 

_get_associated_game_ids() is a private method as it is an internal helper function to get all data for one season. That function is the following:

{% highlight python %}
download_play_by_play_data_for_season(self, season: str, game_type:str)
{% endhighlight %}

Using this method we can retrieve all data for a single season/game-type specified. We can then effeciently loop through all combinations of seasons and playoffs needed and retrieve all their data. We achieve this in the following accessbile function:

{% highlight python %}
download_all_play_by_play_data(self, seasons:list, game_types:list)
{% endhighlight %}

where seasons is a list of seasons and game_types list of all data needed. Example usage:

{% highlight python %}
from dataAcquisition import DataAcquisition

data_aquirer = DataAcquisition()
seasons = ['20162017', '20172018', '20182019', '20192020', '20202021']
game_types = ['R', 'P']

data_aquirer.download_all_play_by_play_data(seasons, game_types)
{% endhighlight %}

All JSONs will be downloaded under a "data/" directory under your current directory.


## 2. Interactive Debugging Tool
*    The widgets has been made by ipywidgets library and widgets.


    game_type = widgets.Dropdown(
    options = ['Regular', 'Play_off'],
    description = 'Type of the game :',
    disabled = False
    )
    def handle_game_type(change):
        new_value = change.new


    year_of_the_game = widgets.Dropdown(
        options = [2016, 2017, 2018, 2019, 2020],
        description = 'year of the game',
        disabled = False
    )
    def handle_year_of_the_game(change):
        new_value = change.new

    game_id = widgets.IntSlider(
        min= 1,
        max = 1271,
        description='game number',
        disabled=False
    )
    def handle_game_id(change):
        new_value = change.new

    event = widgets.IntSlider(
        min= 1,
        max = 100,
        description='events',
        disabled=False,
    )
    def handle_event(change):
        new_value = change.new


   

*    placing the widgets in a right order.

    inters = widgets.VBox([widgets.HBox([game_type, year_of_the_game]),widgets.HBox([game_id, event])])

*   Obtaining the exact event from entries and creating the adresses 


    serial_number = 20000 if game_type == 'Regular' else 30000
    json_file = f'{year_of_the_game}0{int(serial_number) + int(game_id)}'
    gtype = 'R' if game_type == 'Regular' else 'P'


    

*   Opening data json file
    with open(f'data/{year_of_the_game}/{gtype}/{json_file}.json') as f:
        game_info = json.load(f)
    f.close()

    

*   obtaining the information from json:

        home_team = game_info['gameData']["teams"]["home"]["abbreviation"]
        away_team = game_info['gameData']["teams"]["away"]["abbreviation"]
        home_team_goal = game_info['liveData']["linescore"]["teams"]["home"]["goals"]
        away_team_goal = game_info['liveData']["linescore"]["teams"]["away"]["goals"]
        home_team_goal_shots_on_goal = game_info['liveData']["linescore"]["teams"]["home"]["shotsOnGoal"]
        away_team_goal_shots_on_goal = game_info['liveData']["linescore"]["teams"]["away"]["shotsOnGoal"]
        home_team_so = game_info['liveData']["linescore"]["shootoutInfo"]["home"]["scores"]
        away_team_so = game_info['liveData']["linescore"]["shootoutInfo"]["away"]["scores"]
        home_team_attempts = game_info['liveData']["linescore"]["shootoutInfo"]["home"]["attempts"]
        away_team_attempts = game_info['liveData']["linescore"]["shootoutInfo"]["away"]["attempts"]
        event_time = game_info['liveData']['plays']['allPlays'][event]["about"]["periodTime"]
        event_des = game_info['liveData']['plays']['allPlays'][event]["result"]["description"]
        period_time = game_info['liveData']['plays']['allPlays'][event]["about"]["periodTime"]    
        period = game_info['liveData']['plays']['allPlays'][event]["about"]["period"]
        home_data = pd.DataFrame({'Home':[home_team, home_team_goal, home_team_goal_shots_on_goal, home_team_so, home_team_attempts],
                                'Away':[away_team, away_team_goal, away_team_goal_shots_on_goal, away_team_so, away_team_attempts]
                                }, index= ['Teams:','Goals:','Shots on goal:','SO:','Attempts'])
    * Printing the useful information


        print(f"game_id : {game_info['gamePk']}")
        print(f"total games : {len(os.listdir(f'data/{year_of_the_game}/{gtype}'))}")
        print(f"total events : {len(game_info['liveData']['plays']['allPlays'])}")
        print(f"date time {game_info['gameData']['datetime']['dateTime']}")
        print(home_data)
    
*   Creating the figures 

        fig = plt.figure(figsize=(8, 4))
        img = mpimg.imread('imgs/nhl_rink.png')
        fig, ax = plt.subplots()
        ax.imshow(img,extent=[-100, 100, -42.5, 42.5])
        plt.xlim((-100, 100))
        plt.ylim((-42.5, 42.5))
        my_y_ticks = np.arange(-42.5, 42.5, 21.25)
        plt.yticks(my_y_ticks)
        plt.xlabel('feet')
        plt.ylabel('feet')


        if period % 2 == 1:
            plt.title(f'{event}' + '\n' + f'{period_time}' + f'{period}' + '\n'+ f'{away_team}' + '      VS    ' + f'{home_team}')
        else:
            plt.title(f'{event}' + '\n' + f'{period_time}' + f'{period}' + '\n'+ f'{home_team}' + '      VS    ' + f'{away_team}')

        cors = game_info['liveData']['plays']['allPlays'][event]['coordinates']



        try:
            x, y = cors['x'], cors['y']
            plt.plot(x, y, 'bo')
            plt.annotate(' <'+str(x)+', '+str(y)+'>', xy=(x, y))
        except:
            plt.text(-23, 45, "No ball included !", c='r')

        plt.show()
        pprint.pprint(game_info['liveData']['plays']['allPlays'][event]['result'])


    The tool in this part is an interactive tool to see the game information.
    
     It contains the type of the game that we can choose the type base on play off and regular.
     
    Year of the game that contains years of 2016, 2017, 2018, 2019, 2020. The index bar is indentifier of the game. The index bar on the right is counter of the events in a game.


    After choosing the game based on the specifications, we get the information related to the game and the map of the event where and when it happened.
    
     Also we can see who made the event and what is the result.


<img src="/Blog-post/figures/info.png"><br>

<img src="/Blog-post/figures/eventmap.png"><br>



    here we have the game mode "Play off", in 2019, game number 174, event 54.

## 3. Tidy Data

### Data Snippet

![Insert screenshot of final dataframe here using head(10)](/Blog-post/assets/images/dataframe.png)

### Determining On-Ice Strength for Shots and Goals

A team's strength can fluctuate due to penalties, leading to power play opportunities or being short-handed. Here's an approach to determine the on-ice strength for each shot or goal:

1. **Initialize Counters**: 
   For each shot or goal event, start by initializing two counters, both set to 5. This represents even strength (5 on 5, excluding goalies).

2. **Assess Recent History**:
   Read the `dateTime` attribute of the shot or goal and look backward in the `liveData` dictionary until you find an event that occurred more than 5 minutes prior. This 5-minute window captures any penalties that could affect the on-ice strength.

3. **Handle Penalties**:
   - For events of type `PENALTY` that are labeled as major penalties, identify the penalized team.
   - Decrease the counter for that team by 1, irrespective of any goals scored during the penalty. 
   **Handle Minor Penalties**:
   - If there's an event of type `PENALTY` that's labeled as a minor penalty, check if its `dateTime` is within 2 minutes of the current shot or goal event.
   - If it's within this 2-minute window, determine the penalized team. Decrease the counter for that team by 1. If it's outside this window, the penalty has expired, and you can ignore it.

4. **Assign Strength**:
   Create the `strength` attribute for each shot or goal by displaying the counters of both teams. For instance, if Team A is shooting on Team B, and the counters are 4 and 5 respectively, the strength would be represented as "4 on 5".

### Additional Features from the Dataset

From the available dataset:

1. **Rebound Shots**: Identify a rebound shot by observing two consecutive shots from the same team that happen quickly and are close in location. The subsequent shot can be labeled as a rebound.
2. **Rush Shots**: Classify a shot as a "rush shot" if it occurs shortly after a defensive event for the same team, indicating rapid puck movement from the defensive to offensive zone.
3. **Zone Time Before Shot**: Measure the duration a team spends in the offensive zone before taking a shot. It can highlight a team's possession and pressure abilities. Track events like offensive zone "FACEOFF" wins or "TAKEAWAY" to start the timer, and stop it at the next shot event.


## 4. Simple Visualizations 

### Question 1: Comparing The Shot Types Over All Teams
![comparing the shot types over all teams](/Blog-post/assets/images/shotTypes.png)
#### Description:
From the provided chart, the shot types are categorized by their frequency (count) and the associated goal rate (percentage of shots that result in a goal).

**Most Common Shot Type:** The 'Wrist Shot' is the most common shot type as its count surpasses all other shot types by a significant margin.

**Most Dangerous Shot Type:** Based on goal rate, the 'Tip in' shot type appears to be the most dangerous in season 2020-2021, with a goal rate of 21.98%. 

#### Discussion:

Wrist shots are the most frequently used shot type, which might be due to the fact that they can be executed quickly and require less space compared to other shots. They are versatile and can be taken from various angles and positions on the ice.

However, The 'Tip in' shots have the highest goal rate. This makes sense as tip-ins involve players redirecting a shot.

---

### Question 2: Analysis of Conversion Rate and Total Shots by Shot Distance

---

**Note on Shot Distance Calculation**:

When calculating the distance of shots, we've based our methodology on a typical result observed in NHL matches. Specifically, the coordinates of goals scored right at the goal line appear to be more like `(84,0)` for North American matches. For a detailed reference, you can review this [discussion on RapidMiner Community](https://community.rapidminer.com/discussion/44904/using-the-nhl-api-to-analyze-pro-ice-hockey-data-part-1).

Furthermore, based on NHL statistics, it's assumed that all shots are aimed at the nearest goal. This assumption aligns with observations and data from the NHL, as detailed in this [OMHA article on the science of scoring](https://www.omha.net/news_article/show/667329-the-science-of-scoring).

---

![Season 2018-2019](/Blog-post/assets/images/20182019.png)
![Season 2019-2020](/Blog-post/assets/images/20192020.png)
![Season 2020-2021](/Blog-post/assets/images/20202021.png)
#### Conversion Rate vs Shot Distance:

**Close to Goal**:
- Shots taken between 0-10 feet from the goal have a high conversion rate of around 20%.
  
**Mid-Range Shots**:
- As players shoot from further out, the conversion rate drops significantly. 
  
**Long Shots**:
- Beyond 35 feet, the conversion rate is relatively stable. At distances of 80 meters and beyond, the rate is nearly zero, but there's a noticeable spike between 85-95 meters.

#### Total Shots vs Shot Distance:

**Most Popular Distance**:
- The majority of shots are taken from 5-10 feet.
  
**Steady Range**:
- Between 15-55 feet, the number of shots remains fairly consistent.
  
**Rare Long Shots**:
- Shots from distances greater than 80 meters are uncommon, which aligns with the low conversion rates observed from those distances.

#### Summary:

The shot patterns and conversion rates have been consistent over the past three seasons. The reason we chose this graph is that the graph effectively displays these trends and by juxtaposing the shot count with the conversion rate, the visualization effectively dispels potential misconceptions — like a low shot count yielding an anomalously high conversion rate.


### Question 3: Analysis of Goal Rate and Shots Types by Shot Distance

---

**Note on Data Representation and Filtering**:

In creating this plot, we have employed simple descriptive statistics (e.g., the median or the 25th percentile of shot counts) to represent the goal percentages for each shot type across various distances. Importantly, to ensure the accuracy and prevent potential misinterpretations of the results, we have set a fixed threshold for the number of shots taken at a specific distance.

Specifically, only shot types with a count greater than 20 at a particular distance have been included in the graph. This threshold was set to avoid visualizing shot types with low sample sizes, which could produce misleading insights or overemphasize rare occurrences.

```python
threshold = 20
grouped_type = grouped_type[grouped_type['total_shots'] > threshold]
```

---

![comparing the shot types and distance](/Blog-post/assets/images/function_shot_distance.png)
#### Finding:

**High Goal Percentage**: 
- The "Slap Shot" is the most effective when taken from both close and medium distance range (0-35). Its goal rate is the highest among that range.  So that it appears to be the most dangerous shot type.

**Medium To Long Distance Shots**: 
- The "Tip in" shots shows effectiveness at the range of 40-60 feet , with a higher goal percentage than others. 
- The "Wrist Shot" has a higher likelihood of resulting in goals

**Consistency Across Distances**: 
- "Slap Shot" and "Snap Shot" have relatively consistent goal rates across various distances, especially from 10-55. Their consistency might make them reliable shot choices in many game situations


## 5. Advanced Visualizations: Shot Maps

<b>Shot Maps for 2016-2017 Season</b><br>

<iframe src="/Blog-post/html/shot_map_2016-2017.html" height="600px" width="100%" style="border:none;"></iframe>

<b>Shot Maps for 2017-2018 Season</b><br>

<iframe src="/Blog-post/html/shot_map_2017-2018.html" height="600px" width="100%" style="border:none;"></iframe>

<b>Shot Maps for 2018-2019 Season</b><br>

<iframe src="/Blog-post/html/shot_map_2018-2019.html" height="600px" width="100%" style="border:none;"></iframe>

<b>Shot Maps for 2019-2020 Season</b><br>

<iframe src="/Blog-post/html/shot_map_2019-2020.html" height="600px" width="100%" style="border:none;"></iframe>

<b>Shot Maps for 2020-2021 Season</b><br>

<iframe src="/Blog-post/html/shot_map_2020-2021.html" height="600px" width="100%" style="border:none;"></iframe>

<b>Interpretting the Shot Maps</b><br>

* The season shotmaps above show us the rate of team shots and heatmap of their shots. What we can clearly see from these interactive figures is that most of the teams shoot when they are near the net. Another observation is that the some of the teams shoot from the sides while some teams such as Vancuver canucks shoot when they are at the middle. Feel free to interact with the above figures, pick your favourite team and track their shot patterns accross the 5 seasons!

<b>Discussion on Colorado Avalanche</b><br>

* During the 2016-2017 season, the Colorado Avalanche displayed a notably reduced shot frequency in the near area of the net, approximately 15-25 feet away from it, in contrast to the league's standard shot frequency from the same spot.

    In the 2020-2021 season, the Colorado Avalanche had a different way of play-style, as they showed a higher-than-average shot frequency near the net, indicating a significant difference in their approach to the game. This probably had a direct hand in why they performed drastically better in the 2020-2021 season compared to the 2016-2017 season.

<b>Buffalo Sabres VS Tampa Bay Lightning</b><br>

* Shot Range:

    Both teams tend to take shots in the near-to-mid-range area, which is 10 to 50 feet away from the net. This suggests that they prefer quality scoring opportunities rather than long-range attempts.
    Buffalo Sabres:

    The Sabres show a relatively balanced approach in terms of shot distribution on the left and right sides of the net.
    They tend to have fewer shots in the middle position, which could indicate a preference for shooting from the sides.
    This pattern may suggest that the Sabres are trying to create scoring chances from various angles.
    Tampa Bay Lightning:

    The Tampa Bay Lightning's shot map reveals a concentration of shots in the middle position.
    They appear to have a strategic focus on the high-scoring central area in front of the net.
    The Lightning takes fewer shots from the sides, indicating that they rely more on plays through the center, possibly exploiting opportunities in front of the net.

    Buffalo's approach of distributing shots across the left and right sides might be an attempt to make their attack more diverse, taking advantage of opportunities that arise on both sides.
    Tampa Bay's emphasis on the middle position may reflect a strategy to capitalize on high-percentage scoring chances in the most critical area in front of the net.

    Overall, The Lightning's success could be attributed to their strategy of capitalizing on high-percentage scoring opportunities in front of the net. Their focus on the middle position indicates a strong commitment to effective offensive plays and converting these chances into goals.


    The shot distribution observations provide valuable insights, but they do not offer a comprehensive explanation for a team's performance. For instance we do not have any information about team chemistry, coaching, and leadership.

## Milestone 2

[Milestone 2](./Blog-post/_posts/2023-11-15-milestone2.md)


---
layout: post
title:  "IFT 6758 Project: Milestone 2"
subtitle: "Six Subtitle"
date:   2023-11-11
---


## 1. Feature Engineering I
<b> List of Added Features</b><br>
<ol>
    <li> <b> Shot_distance_to_goal :</b> Distance of the shot to the goal </li>
    <li> <b> angle :</b> Angle of shot to the center of goal</li>
    <li> <b> goal_rate_dist :</b> Represents the ratio of the number of goals to the total number of events relative to distance (#goals / (#no_goals + #goals), to the distance) </li>
    <li> <b> goal_rate_angle :</b> Represents the ratio of the number of goals to the total number of events relative to angle  (#goals / (#no_goals + #goals), to the angle) </li>
    <li> <b> is_goal :</b> was the shot a goal or not</li>
</ol>
<b>Bars of distance and angle</b>

![Shot counts - distance](/Blog-post/assets/images/shotcountsdistance.png)

    
<b>left graph :</b>
The histograms illustrating shot counts in relation to goal outcomes, based on the dataset covering the 2016/17 to 2019/12 regular seasons, reveal a noticeable trend. As the distance from the net increases beyond 50 feet, there is a significant decrease in the number of shots on goal.
based on the graphs there are not so many chances to shoot in a very near of the goals.
This observed pattern may be attributed to the inherent challenges associated with longer shot distances. The probability of success for the shooter diminishes as the distance to the goal increases, potentially due to a combination of reduced accuracy and longer reaction times for goaltenders. The data suggests that shots from greater distances pose a greater challenge for both the offensive and defensive players on the ice. Also the number of goals we decreased by increase of distance. 
     
<b>right graph :</b>
a prevalent trend emerges where shooters frequently opt for two primary angles: a direct shot straight to the net or an angle of approximately +/-30 degrees. However, the most successful goals are observed when shots are taken straight to the net. Beyond an angle of +/-30 degrees, there is a discernible decline in the frequency of scoring. This pattern underscores a preference for direct and moderately angled shots, suggesting a strategic inclination among shooters to optimize goal-scoring opportunities within specific angular ranges.
      
      
<b>Histograms of shot counts for distance and angle</b> 
![distance - angle](/Blog-post/assets/images/Angledistance.png)
    
The 2D scatter plot and accompanying histograms depicting shot counts concerning both distance and angle offer a nuanced view of shooter behavior in the dataset.

Examining the 2D histogram, a clear trend emerges: as the distance to the goal decreases, shooters are more inclined to opt for wide-angle shots. Conversely, when positioned farther from the net, there is a propensity to take shots at a slight angle.

Remarkably, areas characterized by the highest frequency of shooting attempts are identified. These hotspots include the immediate vicinity of the goal, regions approximately 50 feet away from the net, and angles at approximately +/-30 degrees. This observation underscores specific zones on the ice where shooters are more likely to concentrate their attempts, shedding light on strategic preferences in shot selection.

 <b>Histograms of goal rate</b> 

![distance - rate](/Blog-post/assets/images/distancerate.png)

![Shot counts - angle](/Blog-post/assets/images/anglerate.png)

The two Line charts depicting goal rates as a function of both distance and angle to the net provide a comprehensive overview of scoring tendencies in the dataset.

Consistent with previous observations, a clear trend emerges: as shooters approach the net, and the angle of the shot decreases, there is a notable increase in the likelihood of scoring a goal. In other words, proximity to the net and a more direct shot trajectory are positively correlated with a higher goal-scoring rate.

This finding aligns with the intuitive understanding that shooters have a greater chance of success when in close proximity to the goal, and when their shots follow a more direct path angle ([-18,+18]). The charts reinforce the notion that strategic positioning and shot selection, emphasizing shorter distances and smaller angles, play pivotal roles in enhancing the effectiveness of goal-scoring attempts. These insights contribute valuable information for understanding the nuanced dynamics of scoring in hockey based on shot distance and angle.
 <b>Histograms of empty and nonempty nets</b> 

![empty](/Blog-post/assets/images/distancegoalempty.png)

![non empty](/Blog-post/assets/images/distancegoalnonempty.png)


The two histograms offer insights into the distribution of goals scored based on whether the net was empty or occupied. A conspicuous disparity lies in the distance at which goals are scored in these two scenarios. Notably, goals scored in a non-empty net tend to occur in close proximity to the goal. In stark contrast, when the net is empty, shooters demonstrate a higher likelihood of scoring from virtually any location on the court and it makes sense.
</ol>


## 2. Baseline Models

In this section, we evaluate the performance of baseline logistic regression models trained on different features of our dataset. The models were trained using only the 'distance' feature, only the 'angle' feature, and both 'distance' and 'angle' features combined.

### Baseline Model Trained on Distance

![Confusion Matrix](/Blog-post/assets/images/conf_matrix_distance.png)

The basic logistic regression model, utilizing solely the 'distance' feature, achieved an accuracy of 0.9086. Look at the above confusion matrix, we can see that the model did not predict any positive classes, failing to identify any goals. This outcome might point to issues related to class imbalance or the limited predictive power of the 'distance' feature.

### Baseline Models Trained on Angle and Both Features

Subsequent models trained on the 'angle' feature and both 'distance' and 'angle' features did not significantly improve the predictive performance, indicating that these features alone might not be sufficient for the task at hand.

### Visualization and Interpretation

The performance of these baseline models can be visually interpreted through the following plots:

![ROC Curve Comparison](/Blog-post/assets/images/roc_curve_plot.png)

The ROC curve comparison illustrates that while there is some ability to distinguish between the classes, the discriminative performance of the feature of distance is greater than that of the angle feature, and has nearly the same results obtained by using both feature

![Goal Rate vs Probability Percentile Plot](/Blog-post/assets/images/goal_rate_plot.png)

The plot depicting the goal rate against the probability percentile conveys a consistent pattern: higher probabilities predicted by the model correlate with an increased likelihood of actual goal occurrences. This reinforces the earlier inference where the 'distance' attribute outperforms the 'angle' attribute, and has a nearly identical performance as using the combination of both features.

![Cumulative Goals Plot](/Blog-post/assets/images/cumulative_goal_rate_plot.png)

The graph detailing the cumulative proportion of goals underscores a recurring observation: the predictive strength of the angle feature is overshadowed by that of the distance feature. Yet again, amalgamating both features delivers a nearly identical level of discrimination.

![Calibration Curve Plot](/Blog-post/assets/images/calibration_curve_plot.png)

Calibration curves serve as a metric to gauge the precision of a classifier's probability estimations. A visual inspection of these curves indicates a general trend of suboptimal calibration across the models, likely attributable to data imbalance. The angle feature, when isolated, exhibits modest reliability, whereas its combination with the distance feature enhances dependability. This plot also validates the positive correlation between the distance feature and the model's scoring accuracy.

To encapsulate, the distance attribute emerges as a pivotal factor for the model's efficiency. When paired with the angle attribute, the model's efficacy is modestly amplified. In contrast, the angle attribute, on its own, exhibits a tendency to align with the random baseline rather than displaying substantial discriminative capacity.

The three models can be found under the 'models' directory within the specific Comet.ml project entry.

- **Angle Model**: The logistic regression model trained exclusively on the angle feature.
- **Distance Model**: The logistic regression model trained solely on the distance feature.
- **Combined Model**: The logistic regression model that utilizes both distance and angle features for prediction.

The models are accessible through the following Comet.ml project entry:
[Comet.ml Project: NHL Data Science](https://www.comet.com/mahmoodhegazy/nhl-data-science/916f8c382bc04495adeeef4cf15b98e9?experiment-tab=assetStorage)
### Discussion

The baseline logistic regression models provided a starting point for understanding the predictive capability of individual features. However, their performance indicates the need for more complex models or additional features to capture the nuances of the dataset effectively. Future steps would involve exploring more sophisticated models or feature engineering techniques to improve the predictive performance.



## 3. Feature Engineering II

<b> List of Added Features</b><br>

<ol>
    <li> <b>gameID_eventID :</b> Event_Game ID for identifying unique events (PK)</li>
    <li> <b>game_period :</b> current period of the game.</li>
    <li> <b>game_seconds :</b> Total number of seconds elapsed in the game</li>
    <li> <b>x_coordinate :</b> shot x coordinate</li>
    <li> <b>y_coordinate :</b> shot y coordinate</li>
    <li> <b>shot_distance_to_goal :</b> distance between x,y coordinates of the shot and the net</li>
    <li> <b>shot_angle :</b> the shot angle.</li>
    <li> <b>shot_type :</b> type of shot</li>
    <li> <b>last_event :</b>  last event type</li>
    <li> <b>last_x_coordinate :</b> last event x coordinate</li>
    <li> <b>last_y_coordinate :</b> last event y coordinate</li>
    <li> <b>distance_from_last_event :</b> distance between x,y coordinates of current event and last event</li>
    <li> <b>time_from_last_event :</b> time passed in seconds since the last event</li>
    <li> <b>rebound :</b> Indicator of whether or not this is a rebound shot. Will be True on the 2nd successive shot, otherwise False.</li>
    <li> <b>speed :</b>  the distance from the previous event divided by the time since the previous event (distance_from_last_event/time_from_last_event).</li>
    <li> <b>change_in_shot_angle :</b> Represents the difference in the angles of consecutive shots relative to the goal. Specifically, it measures the deviation between the angle formed by the last shot and the goal, and the angle formed by the current rebound shot and the goal </li>
    <li> <b>time_since_powerplay_started :</b>  indicates the number of seconds that have passed since the beginning of a power-play. This timer resets to zero once the power-play concludes. </li>
    <li> <b>num_friendly_non_goalie_skaters :</b> denotes the count of skaters from the shooter's team present on the ice, excluding the goalie</li>
    <li> <b>num_opposing_non_goalie_skaters :</b> denotes the count of skaters from the opposing team present on the ice, excluding the goalie</li>
 
</ol>

<b>Comet.ml link storing the required experiment dataframe (wpg_v_wsh_2017021065):</b><br>

<a href="https://www.comet.com/mahmoodhegazy/nhl-data-science/9d2048b8c5d8422db2a2e4ee3551d5c9"> https://www.comet.com/mahmoodhegazy/nhl-data-science/9d2048b8c5d8422db2a2e4ee3551d5c9 </a>

## 4. Advanced Models

### Q1 Baseline
At first we select these features  ['x_coordinate', 'y_coordinate', 'last_x_coordinate',
       'last_y_coordinate', 'distance_from_last_event', 'last_event',
       'rebound', 'speed', 'time_since_powerplay_started',
       'num_friendly_non_goalie_skaters', 'num_opposing_non_goalie_skaters',
       'is_emptyNet', 'shot_type', 'shot_distance_to_goal',
       'shot_angle', 'change_in_shot_angle']
  
For the first part we only used shot distance and shot angle for training the model. We used 2016/17 to 2018/19 for training. This dataset then splited by train_test_split in sklearn library to training and validation set. 

In the initial phase, the model was trained using only shot distance and shot angle. The data from the 2016/17 to 2018/19 regular seasons served as the training dataset. This dataset was then divided into training and validation sets using the `train_test_split`  function from the sklearn library.

#### Results:

![Roc-Auc](/Blog-post/assets/images/Q1.5roc.png)

The Receiver Operating Characteristic (ROC) curve is a graphical representation that illustrates the trade-off between true positive rate (sensitivity) and false positive rate (specificity) across different probability thresholds. It is commonly used to assess the performance of classification models.

![rate](/Blog-post/assets/images/Q1.5rate.png)

Comparing goal rate against probability percentiles involves plotting the cumulative proportion of goals scored against the probability assigned by a predictive model. This curve provides insights into the model's ability to discriminate between instances that result in goals and those that do not, offering a nuanced view of its predictive accuracy.

![cumulative ](/Blog-post/assets/images/Q1.5cumulative.png)

The cumulative proportion of goals vs. probability percentile curve extends this analysis by visually displaying how the model's predicted probabilities align with the actual cumulative proportion of goals. It helps assess the model's calibration, indicating how well the predicted probabilities correspond to the observed outcomes.

![reliablity](/Blog-post/assets/images/Q1.5reliable.png)

A reliability curve further complements these assessments by plotting the predicted probabilities against the observed outcomes. It offers a visual depiction of the calibration of the model, providing insights into the reliability of the predicted probabilities across the entire range. A well-calibrated model will have points on the reliability curve that align closely with the diagonal, indicating accurate probability estimates.

The XGBoost model outperforms the Logistic Regression in terms of both ROC curve and accuracy. Crucially, the F1 score of XGBoost is 0.6, significantly higher than that of Logistic Regression. This large difference in F1 score is important because it indicates a more balanced performance between precision and recall in XGBoost, suggesting it's more effective in correctly identifying true positives while maintaining a lower rate of false positives and false negatives.

**Comet Link to Experiment**: <a href="https://www.comet.com/mahmoodhegazy/nhl-data-science/e9dd7470c82c4cc6be538c2342409b28">Baseline</a><br>
(All 3 XGBoost models are under this same experiment)

### Q2 Hyperparameter Tuning 
<!-- At first we tuned the 'n_estimators' with [100, 200, 300] and we understood 100 is the best. -->
The approach for hyperparameter tuning was an iterative grid search to try to see the effect of each hyperparameter on our performance. 

Initially, the `n_estimators` parameter, indicating number of learners, was tuned using values 100, 200 and 300. The analysis determined that 100 estimators yielded the best results.
![number of estimators](/Blog-post/assets/images/nestimator.png)

 Subsequently, the focus shifted to tuning the `learning_rate` and `max_depth`. It was found that the optimal settings for these were 0.01 for the `learning_rate` and 8 for `max_depth`.
 ![learning rate](/Blog-post/assets/images/learningrate.png)

 Finally, we optimized for `min_child_weight`, `colsample_bytree`, and `subsample` and we found 1, 0.9, 1 as the optimal params respectively.

#### Hyperparameter Tuned Model Performance:
![Roc-Auc](/Blog-post/assets/images/Q5.2roc.png)
![rate](/Blog-post/assets/images/Q5.2.5rate.png)
![cumulative ](/Blog-post/assets/images/Q5.2cumulative.png)
![reliablity](/Blog-post/assets/images/Q5.2reliable.png)

**Comet Link to Experiment**: <a href="https://www.comet.com/mahmoodhegazy/nhl-data-science/e9dd7470c82c4cc6be538c2342409b28">Hyperparameter Tuned Model</a><br>

### Q3 Feature Selection 


We experimented with four distinct methods for feature selection: correlation matrix, feature importance as provided by XGBoost, SHAP values, and Recursive Feature Addition. 

#### Correlation Matrix:
![Correlation matrix](/Blog-post/assets/images/corr.png)

#### Feature Importance as provided by XGBoost:
![Feature importance](/Blog-post/assets/images/importance.png)

#### SHAP values:
![Shap](/Blog-post/assets/images/shap.png)

#### Recursive Feature Addition:

We found that the most effective approach was found to be **Recursive Feature Addition**, and thus, it will be the only results and visualizations shown. The method found the following features to be optimal:

- `game_seconds`
- `game_period`
- `y_coordinate`
- `shot_distance_to_goal`
- `shot_angle`
- `time_from_last_event`
- `distance_from_last_event`
- `rebound`
- `speed`
- `time_since_powerplay_started`
- `num_friendly_non_goalie_skaters`
- `num_opposing_non_goalie_skaters`
- `last_event`
- `shot_type`

##### **Best Model Performance results and visualizations**: 

![Roc-Auc](/Blog-post/assets/images/bestroc.png)
![rate](/Blog-post/assets/images/bestrate.png)
![cumulative ](/Blog-post/assets/images/bestcumulativ.png)
![reliablity](/Blog-post/assets/images/bestreliable.png)

##### Brief dicussion:

The ROC curve of the model shows a substantial improvement over the baseline, with the Area Under the Curve (AUC) increasing by 0.2. This enhancement in AUC signifies a much better model, as it indicates a greater ability to distinguish between goals and shots effectively.
Moreover, the goal rate increse from 0.4 to 1, the cumulative proportion had a rise and it is a more reliable model.

**Comet Link to Experiment**: <a href="https://www.comet.com/mahmoodhegazy/nhl-data-science/e9dd7470c82c4cc6be538c2342409b28">Best XGboost Model</a><br>

## 5. Other/Best Shot Models


### Experiments Setup (Same accross all experiments)

<b>Training Data</b> - All data for <b>regular</b> seasons 2016/17 - 2018/19.<br><br>

All Experiments have a pipeline created through the <b>`create_pipeline`</b> function found in other_ml_models.py. It is a versatile tool for building a complete machine learning pipeline, handling preprocessing (both numerical and categorical), optional feature selection, and model fitting in a streamlined and efficient manner. This setup is especially useful for ensuring consistency in data transformations across both training and testing datasets. The breakdown is as follows:

##### **Setting Up Encoders Choice**
- Initializes a dictionary `encoders` with `OrdinalEncoder` (default) and `OneHotEncoder`. 

##### **Creating Transformers**
- `numeric_transformer`: Processes numerical data by imputing missing values and scaling.
- `categorical_transformer`: Processes categorical data by imputing missing values and applying the chosen encoder.

##### **Column Transformer**
- `preprocessor`: A `ColumnTransformer` that applies the correct transformations to numerical and categorical columns.

##### **Building the Full Pipeline**
- Constructs a `Pipeline` object with the preprocessing steps, optional feature selection, and the classifier.

### Hyperparameter tunning Methodology
- Sci-kit learn's `GridSearchCV`  was used to perform Grid Search with 3-fold Cross-Validation across a pred-defined hyperparameter space (defined according to model). The method searchs through the specified subset of hyperparameters for a model and finds the most effective combination. The best model is then used for training and validation.

### Feature Selection Methodology
- Sci-kit learn's `RFECV` (Recursive Feature Elimination with Cross-Validation) was deployed on all algorithms to find the best features per model. It is a feature selection method that iteratively fits a model and removes the least important features based on certain criteria, using cross-validation to assess model performance at each step. This process continues until the optimal number of features is reached, ensuring that the selected features contribute most effectively to the model's predictive accuracy.

### Various Techniques Discussion

#### Random Forest 
Random Forest Classifiers are an ensemble learning method that operate by constructing a multitude of decision trees (weak learners) at training time, leading to improved accuracy and robustness to overfitting. They make predictions taking the majority vote across these diverse trees. It performed very well on the validation set with a **94.69%** accuracy. It was the 2'nd best performer among all classifiers. This was expected as Random Forests are very good at capturing non-linear relationships between features, which is often the case in complex scenarios like sports events where the outcome (goal or no goal) can depend on a multitude of interrelated factors.

##### **Experiment Link**

<a href="https://www.comet.com/mahmoodhegazy/nhl-data-science/34144ddb714e4845be497ce0e144f098">Random_Forest_Best_Shot</a><br>

##### **Pipeline**

![image](/Blog-post/assets/images/rf_pipe.png)

##### **Feature Selection and Importance** : 

![image](/Blog-post/assets/images/rf_best_features.png)

##### **ROC/AUC curve**

![image](/Blog-post/assets/images/rf_roc.png)

##### **Precesion-Recall curve**

![image](/Blog-post/assets/images/rf_prec_rec.png)

##### **Goal Rate vs probability percentile plot**

![image](/Blog-post/assets/images/rf_goal_rate.png)

##### **Cumulative proportion of goals vs probability percentile plot**

![image](/Blog-post/assets/images/rf_cumulative_goal.png)

##### **Reliability Curve**

![image](/Blog-post/assets/images/rf_calib.png)


#### CatBoost
With some intuition from Part 5 that Boosting algoriths might work well in this task, another high-performance open source library for gradient boosting on decision trees, CatBoost, was leveraged. CatBoost is particularly effective at processing categorical data. And since from our RF experiment we know that both `shot_type` and `last_event` (our only 2 categorical features) were in the top 4 important features, we thought to try CatBoost out. It performed the **best** amongst all models with a validation accuracy of **94.78%**.

##### **Experiment Link**

<a href="https://www.comet.com/mahmoodhegazy/nhl-data-science/5099680072f7468a9e7d2cec05526378">CatBoost_Best_Shot</a><br>

##### **Pipeline**

![image](/Blog-post/assets/images/cat_pipe.png)

##### **Feature Selection and Importance** : 

![image](/Blog-post/assets/images/cat_best_features.png)

##### **ROC/AUC curve**

![image](/Blog-post/assets/images/cat_roc.png)

##### **Precesion-Recall curve**

![image](/Blog-post/assets/images/cat_prec_rec.png)

##### **Goal Rate vs probability percentile plot**

![image](/Blog-post/assets/images/cat_goal_rate.png)

##### **Cumulative proportion of goals vs probability percentile plot**

![image](/Blog-post/assets/images/cat_cumulative_goal.png)

##### **Reliability Curve**

![image](/Blog-post/assets/images/cat_calib.png)



#### K-Nearest-Neighbours

K-Nearest Neighbors (KNN) is a supervised learning algorithm that classifies or predicts the group of a data point based on the proximity to its nearest neighbors in the dataset, operating without the need for predefined parameters. It performed well but was the weakest amongst the the afore-mentioned (part 6) models.

##### **Experiment Link**

<a href="https://www.comet.com/mahmoodhegazy/nhl-data-science/b80593d676374abb90be80dd5f748c5a">KNN_Best_Shot</a><br>

##### **Pipeline**

![image](/Blog-post/assets/images/knn_pipe.png)

##### **ROC/AUC curve**

![image](/Blog-post/assets/images/knn_roc.png)

##### **Precesion-Recall curve**

![image](/Blog-post/assets/images/knn_prec_rec.png)

##### **Goal Rate vs probability percentile plot**

![image](/Blog-post/assets/images/knn_goal_rate.png)

##### **Cumulative proportion of goals vs probability percentile plot**

![image](/Blog-post/assets/images/knn_cumulative_goal.png)

##### **Reliability Curve**

![image](/Blog-post/assets/images/knn_calib.png)



#### MLP (Multi-layer Perceptron classifier)
The Multilayer Perceptron (MLP) is a type of artificial neural network that operates in a feedforward manner, effectively mapping input data to corresponding outputs. It is composed of multiple layers, with each layer being fully connected to the subsequent one. It performed well but was the weakest amongst all (part 6) models.

##### **Experiment Link**

<a href="https://www.comet.com/mahmoodhegazy/nhl-data-science/713fc623dc8d4c5eb8e54a503cb0638c">MLP_Best_Shot</a><br>

##### **Pipeline**

![image](/Blog-post/assets/images/mlp_pipeline_arch.png)

##### **Precesion-Recall curve**

![image](/Blog-post/assets/images/mlp_prec_rec.png)

##### **ROC/AUC curve**

![image](/Blog-post/assets/images/mlp_roc.png)

##### **Goal Rate vs probability percentile plot**

![image](/Blog-post/assets/images/mlp_goal_rate.png)

##### **Cumulative proportion of goals vs probability percentile plot**

![image](/Blog-post/assets/images/mlp_cumulative_goal.png)

##### **Reliability Curve**

![image](/Blog-post/assets/images/mlp_calib.png)


### Conclusion

Picking the best model is not only looking at accuracy. We have a class imbalance where only ~10% of events are goals and therefore looking into other metrics such as precision and recall is crucial. 
 - Precision measures the accuracy of the positive predictions. In the context of our task, a high precision would mean that when our model predicts a goal, it's very likely to be a goal. This is important in scenarios where the credibility of the prediction is crucial.
 - Recall measures the ability of the model to find all relevant instances of goals. In the context of our task, a high recall would mean that the model is good at identifying shots that are likely to be goals. Favoring recall is ideal when we want to ensure you capture as many potential goal-scoring opportunities as possible, even if it means including more false positives.

 It is important to hit a nice balance between precision and recall and the precision-recall curve with the highest AUC will be the best that strikes that balance. For our case, that is **CatBoost**, which also happens to have the highest accuracy as well.





## 6. Evaluate on test set

## Test on 2019/20 Regular Season Dataset

Our evaluation of the five models on the untouched 2019/20 2020/21 regular season dataset yielded insightful results. While the logistic regression models showed consistent accuracy, they lacked in F1 score, recall, and precision, indicating that they may not be as effective in classifying goals within the dataset. On the other hand, the XGBoost and Cat Boost models not only showed higher accuracy but also performed significantly better across all other metrics, suggesting a more balanced classification capability.

### ROC/AUC Curves
![ROC Curves for All Models - Regular Season](/Blog-post/assets/images/roc_all_models.png)

### Goal Rate vs Probability Percentile
![Goal Rate vs Probability Percentile - Regular Season](/Blog-post/assets/images/all_models_goal_rate.png)

### Cumulative Proportion of Goals vs Probability Percentile
![Cumulative Proportion of Goals - Regular Season](/Blog-post/assets/images/all_models_cumulative_goals.png)

### Reliability Curve
![Combined Calibration Curves - Regular Season](/Blog-post/assets/images/combined_calibration_curves.png)

The models largely mirrored their validation set performance when applied to the untouched test set, maintaining satisfactory levels of accuracy and demonstrating reliable predictive capabilities. This consistency between the validation and test sets reaffirms the robustness of the modeling approach
## Test on 2019/20 Playoff Games

### ROC/AUC Curves
![ROC Curves for All Models - Playoff Games](/Blog-post/assets/images/roc_all_models_playoff.png)

### Goal Rate vs Probability Percentile
![Goal Rate vs Probability Percentile - Playoff Games](/Blog-post/assets/images/all_models_goal_rate_playoff.png)

### Cumulative Proportion of Goals vs Probability Percentile
![Cumulative Proportion of Goals - Playoff Games](/Blog-post/assets/images/all_models_cumulative_goals_playoff.png)

### Reliability Curve
![Combined Calibration Curves - Playoff Games](/Blog-post/assets/images/combined_calibration_curves_playoff.png)

### Summary Metrics

The table below summarizes the performance metrics of each model across both regular and playoff datasets.

| Model | Accuracy (Regular) | F1 Score (Regular) | Recall (Regular) | Precision (Regular) | Accuracy (Playoff) | F1 Score (Playoff) | Recall (Playoff) | Precision (Playoff) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Logistic Regression Distance | 0.9030 | 0.0000 | 0.0000 | 0.0000 | 0.9123 | 0.0000 | 0.0000 | 0.0000 |
| Logistic Regression Angle | 0.9030 | 0.0000 | 0.0000 | 0.0000 | 0.9123 | 0.0000 | 0.0000 | 0.0000 |
| Logistic Regression Both | 0.9030 | 0.0000 | 0.0000 | 0.0000 | 0.9123 | 0.0000 | 0.0000 | 0.0000 |
| XGBoost | 0.9401 | 0.5653 | 0.4014 | 0.9557 | 0.9469 | 0.5779 | 0.4145 | 0.9539 |
| Cat Boost | 0.9440 | 0.5972 | 0.4280 | 0.9873 | 0.9512 | 0.6172 | 0.4484 | 0.9898 |

During the playoff games, our models displayed robust generalization, with the XGBoost and Cat Boost models showing improved precision and recall, suggesting their effectiveness in capturing the dynamic nature of playoff hockey. Despite high accuracy, logistic regression models continued to struggle with positive class predictions, indicating a need for more complex models for goal event prediction. The enhanced performance of complex models in playoffs, as seen in ROC/AUC and calibration curves, underscores their reliability in high-stakes scenarios, emphasizing their predictive strength over simpler models.





