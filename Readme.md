# Workout Analytics Dashboard

A comprehensive dashboard for visualizing and analyzing workout data from multiple fitness tracking apps.

## Overview

This application provides an interactive dashboard to track, analyze, and visualize your workout progress over time. It supports data from multiple workout tracking apps including Hevy, Strong, and JeeFit, allowing you to gain insights into your fitness journey regardless of which app you use.

## Features

- **Multi-app Support**: Import and analyze workout data from Hevy, Strong, and JeeFit
- **Interactive Dashboard**: Built with Streamlit for a responsive and user-friendly interface
- **Workout Calendar**: GitHub-style contribution calendar showing workout frequency
- **Exercise Progression**: Track weight and 1RM (one-rep max) progression for specific exercises
- **Weekly Workout Analysis**: Visual representation of workout consistency with weekly blocks
- **Muscle Group Focus**: Analyze which muscle groups you're targeting most frequently
- **Workout Volume Analysis**: Track total volume lifted over time
- **Filtering Capabilities**: Filter data by date range, exercise type, and workout source

## Data Structure

The application works with CSV files from different workout apps:
- `workout_hevy.csv`: Data exported from the Hevy app
- `workout_strong.csv`: Data exported from the Strong app
- `workout_jeefit.csv`: Data exported from the JeeFit app
- `workout_log_jeefit.csv`: Additional log data from JeeFit

## Installation

To run this project locally:

```bash
python3.11 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
```

You may need to install numpy binaries separately depending on your system configuration.

## Usage

Start the dashboard with:

```bash
streamlit run workout_dashboard.py
```

The dashboard will open in your default web browser.

## Dependencies

- streamlit==1.32.0: For creating the interactive web dashboard
- pandas==2.2.1: For data manipulation and analysis
- plotly==5.19.0: For interactive data visualizations
- numpy==1.26.4: For numerical operations
- matplotlib: For creating static visualizations

## Technical Details

The application includes several key components:
- Data loading and preprocessing functions to standardize data from different sources
- Custom visualization functions including calendar heatmaps and weekly blocks
- One-rep max (1RM) calculation using the Epley Formula
- Exercise name standardization to ensure consistent tracking across apps

## License

This project is open-source and available for personal use.
