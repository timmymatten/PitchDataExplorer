"""

MLB Pitcher Data Exploration Dashboard
author: Tim Matten

objective: create a dashboard to help explore dense MLB pitcher data

features: - Scatter Plot of Velocity vs. Spin Rate
          - Line Chart of Pitch Usage Over Time

2024 MLB season pitch data obtained using pybaseball's statcast function...

        from pybaseball import statcast

        data = statcast('2024-01-01', '2024-12-31')
        data.to_csv('savant_data.csv', index=False)



"""

import panel as pn
import pandas as pd
import matplotlib.pyplot as plt
from savant_data_api import SAVANT_DATA_API

# Loads javascript dependencies and configures Panel (required)
pn.extension()

# INITIALIZE API
api = SAVANT_DATA_API()
api.load_data("savant_data.csv")



# WIDGET DECLARATIONS

# Search Widgets
pitcher = pn.widgets.Select(name='Pitcher', options=api.get_pitchers(), value='Cole, Gerrit')

# intial values for the checkboxes to be updated as 'pitcher' widget is updated
initial_pitch_types = api.get_pitch_types(pitcher.value)
# pitches to be shown on scatter plot
pitches = pn.widgets.CheckBoxGroup(name="Pitches", options=initial_pitch_types, value=initial_pitch_types)



# Plotting widgets
width = pn.widgets.IntSlider(name="Width", start=1, end=20, step=1, value=9)
height = pn.widgets.IntSlider(name="Height", start=1, end=20, step=1, value=6)

#Line Chart Widgets
pitch = pn.widgets.Select(name='Pitch', options=api.get_pitch_types(pitcher.value)) # Pitch to be analyzed in line chart




# CALLBACK FUNCTIONS
def get_scatter_plot(pitcher, pitches, width, height):
    """
    returns the scatter plot of velocity vs spin rate for the given pitcher

    pitcher - value in 'player_name' column of savant_data.csv ('Last_First')
    pitches - list of pitch types to be plotted
    width - width of plot
    height - height of plot
    """
    # Get pitcher data
    pitcher_data = api.get_pitcher_data(pitcher)

    # Make sure pitch_type is treated as categorical
    pitch_types = pitcher_data['pitch_type'].unique()
    # create a color mapping that tags pitch types with colors
    colors = plt.cm.tab10(range(len(pitch_types)))
    color_map = dict(zip(pitch_types, colors))

    plt.figure(figsize=(width, height))

    """
    for every pitch type the pitcher throws, put only those pitch types on the 
    plot with its corresponding color. 
    
    full loop will result in a plot with each checked pitch being plotted
    """
    for pitch in pitches:
        subset = pitcher_data[pitcher_data['pitch_type'] == pitch]
        plt.scatter(
            subset['release_speed'],
            subset['release_spin_rate'],
            label=pitch,
            color=color_map.get(pitch, 'gray'),
            alpha=0.7,
            edgecolor='k'
        )

    # plot information
    plt.title(f'Velocity vs. Spin Rate for {pitcher}')
    plt.xlabel('Velocity (mph)')
    plt.ylabel('Spin Rate (rpm)')
    plt.grid(True)
    plt.tight_layout()
    plt.legend(title='Pitch Type')
    return plt.gcf()

# Define a callback that updates the pitch types when pitcher widget changes
def update_pitch_checkboxes(event):
    new_pitch_types = api.get_pitch_types(event.new)
    pitches.options = new_pitch_types
    pitches.value = new_pitch_types  # Optionally select all by default

# Define a callback that updates the pitch type when pitcher widget changes
def update_pitch_select(event):
    new_pitch_types = api.get_pitch_types(event.new)
    pitch.options = new_pitch_types

# create the line chart
def get_line_chart(pitcher, pitch, width, height):
    """
    returns the line chart of pitch usage over time for the given pitcher and pitch

    pitcher - value in 'player_name' column of savant_data.csv ('Last_First')
    pitch - pitch type to be analyzed, given by the pitch widget
    width - width of plot
    height - height of plot
    """

    # Get pitcher data
    pitcher_data = api.get_pitcher_data(pitcher)

    # use datetime
    pitcher_data['game_date'] = pd.to_datetime(pitcher_data['game_date'])
    # filter the specified pitch
    pitcher_data = pitcher_data[pitcher_data['pitch_type'] == pitch]
    # group by date and count the number of pitches
    pitcher_data = pitcher_data.groupby(by='game_date').size().reset_index(name='count')

    # Plot
    plt.figure(figsize=(width, height))
    plt.plot(pitcher_data['game_date'], pitcher_data['count'], marker='o', linestyle='-')
    plt.title(f"Usage of {pitch} Over Time")
    plt.xlabel("Date")
    plt.ylabel("Pitch Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(True)
    return plt.gcf()





# CALLBACK BINDINGS (Connecting widgets to callback functions)
plot = pn.bind(get_scatter_plot, pitcher, pitches, width, height)

# Watch for changes in pitcher widget
pitcher.param.watch(update_pitch_checkboxes, 'value')
pitcher.param.watch(update_pitch_select, 'value')
line = pn.bind(get_line_chart, pitcher, pitch, width, height)

# DASHBOARD WIDGET CONTAINERS ("CARDS")

card_width = 320

search_card = pn.Card(
    pn.Column(
        # Widget 1
        pitcher,
        # Widget 2
        pitches
        # Widget 3
    ),
    title="Scatter Plot Filters", width=card_width, collapsed=False
)


plot_card = pn.Card(
    pn.Column(
        # Widget 1
        height,
        # Widget 2
        width
        # Widget 3
    ),

    title="Plot Size", width=card_width, collapsed=False
)

line_card = pn.Card(
    pn.Column(
        # Widget 1
        pitch
    ),

    title="Line Chart", width=card_width, collapsed=False
)


# LAYOUT

layout = pn.template.FastListTemplate(
    title="Pitcher Data Explorer",
    sidebar=[
        search_card,
        plot_card,
        line_card,
    ],
    theme_toggle=False,
    main=[
        pn.Tabs(
            ("Scatter Plot", plot),  # Replace None with callback binding
            ("Line Chart", line),  # Replace None with callback binding
            active=0  # Which tab is active by default?
        )

    ],
    header_background='#a93226'

).servable()

layout.show()
