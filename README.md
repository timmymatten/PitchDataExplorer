# MLB Pitcher Data Exploration Dashboard

A Python dashboard application for exploring and visualizing 2024 MLB pitcher statistics using interactive plots and filters.

## Overview

This project provides an interactive web-based dashboard to analyze MLB pitcher performance data from the 2024 season. The dashboard features pitch sequencing heatmaps, scatter plots of velocity vs. spin rate, and line charts showing pitch usage over time, with dynamic filtering capabilities.

## Features

- **Pitch Sequencing Heatmap**: Analyze the expected succes rate of a pitch given the previous two pitches in an at bat
- **Interactive Scatter Plot**: Visualize velocity vs. spin rate for selected pitchers and pitch types
- **Line Chart Analysis**: Track pitch usage patterns over the 2024 season
- **Dynamic Filtering**: Filter by pitcher and pitch types with real-time updates
- **Customizable Plots**: Adjust plot dimensions for optimal viewing
- **Clean Interface**: Organized sidebar controls with tabbed main display

## Usage

[Click for Dashboard](https://huggingface.co/spaces/timmymatten8/pitch_data_explorer)

Once the dashboard is running, you can:

1. **Choose Sequence Analysis Type** from the selection box
2. **Select a pitcher** from the dropdown menu in the "Scatter Plot Filters" section
3. **Choose pitch types** to display using the checkbox group
4. **Adjust plot dimensions** using the width and height sliders
5. **Switch between tabs** to view scatter plots or line charts
6. **Analyze pitch usage** over time using the line chart tab

## Data Source

The project uses MLB Statcast data obtained through the `pybaseball` library, covering the entire 2024 MLB season. The data includes detailed pitch-by-pitch information such as:

- Result of a pitch
- Release speed and spin rate
- Pitch types and locations
- Game dates and contexts
- Player information

## Technical Details

### Dependencies
- **Panel**: Web-based dashboard framework
- **Pandas**: Data manipulation and analysis
- **Matplotlib**: Plotting and visualization
- **PyBaseball**: MLB data acquisition

### Data Processing
The `SEQUENCING_API` class handles data cleaning and organization to prepare pitch sequence analysis:
- Load and clean raw Statcast data
- Categorizes pitches by Fastball, Offspeed, Breaking Ball
- Finds every 3-pitch sequence in an at bat
- Creates expectancy matrix for whether the third pitch will be 'successful' given the prior two pitches in the at bat

The `SAVANT_DATA_API` class handles data loading and filtering operations, providing methods to:
- Load and clean raw Statcast data
- Filter data by pitcher and pitch type
- Calculate statistical summaries
- Generate organized data subsets for visualization

### Dashboard Components
- **Sidebar Controls**: Pitcher selection, pitch type filters, and plot customization
- **Tabbed Interface**: Separate views for scatter plots and line charts
- **Reactive Updates**: Automatic refresh of available options when selections change

## Author

Tim Matten

## Notes

- The dashboard is designed to handle the full 2024 MLB dataset, which may contain hundreds of thousands of pitch records
- Initial load time may vary depending on dataset size
