import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import calendar
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Set page config
st.set_page_config(page_title="Workout Dashboard", layout="wide")

# Title
st.title("Workout Analytics Dashboard")

# Function to calculate 1RM using Epley Formula
def calculate_1rm(weight, reps):
    return weight * (1 + reps/30)

# Function to standardize exercise names
def standardize_exercise_name(exercise):
    exercise = exercise.lower()
    if 'lat pulldown' in exercise:
        return 'Lat Pulldown (All Variations)'
    if 'barbell bench press' in exercise or 'bench press (barbell)' in exercise:
        return 'Barbell Bench Press'
    if 'dumbbell bench press' in exercise or 'bench press (dumbbell)' in exercise:
        return 'Dumbbell Bench Press'
    return exercise

# Function to create calendar heatmap
def create_calendar_heatmap(workout_dates, year=None):
    if year is None:
        year = datetime.now().year
    
    # Create a dictionary to store workout counts per day
    workout_counts = {}
    for date in workout_dates:
        date = date.date()
        if date.year == year:
            if date in workout_counts:
                workout_counts[date] += 1
            else:
                workout_counts[date] = 1
    
    # Create a figure and axis with a larger figure size and better spacing
    fig, ax = plt.subplots(figsize=(20, 8))
    plt.subplots_adjust(left=0.05, right=0.95, top=0.90, bottom=0.1)
    
    # Define GitHub-style colors
    colors = ['#ebedf0',  # 0 contributions
             '#9be9a8',   # 1-2 contributions
             '#40c463',   # 3-4 contributions
             '#30a14e',   # 5-6 contributions
             '#216e39']   # 7+ contributions
    
    # Get all dates for the year
    start_date = datetime(year, 1, 1).date()
    end_date = datetime(year, 12, 31).date()
    
    # Calculate the first Sunday before start_date
    while start_date.weekday() != 6:  # 6 is Sunday
        start_date -= timedelta(days=1)
    
    # Calculate the last Saturday after end_date
    while end_date.weekday() != 5:  # 5 is Saturday
        end_date += timedelta(days=1)
    
    # Create calendar grid
    current_date = start_date
    week_num = 0
    
    while current_date <= end_date:
        for day_num in range(7):  # 0 = Sunday, 6 = Saturday
            date = current_date + timedelta(days=day_num)
            
            # Get workout count for the day
            count = workout_counts.get(date, 0)
            
            # Determine color based on count
            if count == 0:
                color = colors[0]
            elif count <= 2:
                color = colors[1]
            elif count <= 4:
                color = colors[2]
            elif count <= 6:
                color = colors[3]
            else:
                color = colors[4]
            
            # Add rectangle for the day
            rect = plt.Rectangle(
                (week_num, 6-day_num),  # Flip y-axis to match GitHub (Monday at top)
                0.9,  # Width slightly less than 1 for spacing
                0.9,  # Height slightly less than 1 for spacing
                facecolor=color,
                edgecolor='white',
                linewidth=1
            )
            ax.add_patch(rect)
            
            # Add month label at the top of the first full week of each month
            if date.day <= 7 and day_num == 6:  # Saturday of first week
                ax.text(week_num, 7.5,
                       date.strftime('%b'),
                       ha='center', va='bottom',
                       fontsize=10, fontweight='bold',
                       color='#666666')
        
        current_date += timedelta(days=7)
        week_num += 1
    
    # Add weekday labels on the left
    weekdays = ['Mon', 'Wed', 'Fri']
    weekday_positions = [5, 3, 1]  # Corresponding to Monday, Wednesday, Friday
    for day, pos in zip(weekdays, weekday_positions):
        ax.text(-0.5, pos,
                day,
                ha='right', va='center',
                fontsize=10,
                color='#666666')
    
    # Set the axis limits with padding
    ax.set_xlim(-1, week_num + 1)
    ax.set_ylim(-1, 8)  # Extra space for month labels
    
    # Remove axis lines and ticks
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Add title
    plt.suptitle(f'Workout Contribution Calendar {year}', y=0.95, fontsize=14, fontweight='bold')
    
    # Add legend
    legend_elements = [
        plt.Rectangle((0, 0), 1, 1, facecolor=colors[0], label='No workouts'),
        plt.Rectangle((0, 0), 1, 1, facecolor=colors[1], label='1-2 workouts'),
        plt.Rectangle((0, 0), 1, 1, facecolor=colors[2], label='3-4 workouts'),
        plt.Rectangle((0, 0), 1, 1, facecolor=colors[3], label='5-6 workouts'),
        plt.Rectangle((0, 0), 1, 1, facecolor=colors[4], label='7+ workouts')
    ]
    ax.legend(handles=legend_elements,
             loc='upper right',
             bbox_to_anchor=(1.0, -0.1),
             ncol=5,
             frameon=False,
             fontsize=10)
    
    return fig

# Function to create weekly blocks view
def create_weekly_blocks(workout_data, min_sessions=3):
    # Get min and max dates
    min_date = workout_data['date'].min()
    max_date = workout_data['date'].max()
    
    # Create a complete date range with all weeks
    date_range = pd.date_range(start=min_date, end=max_date, freq='W')
    complete_weeks = pd.DataFrame({
        'date': date_range,
        'year': date_range.year,
        'week': date_range.isocalendar().week,
        'month': date_range.month,
        'month_name': date_range.strftime('%b')  # Short month name
    })
    
    # Count sessions per week in actual data
    workout_data['week'] = workout_data['date'].dt.isocalendar().week
    workout_data['year'] = workout_data['date'].dt.isocalendar().year
    weekly_sessions = workout_data.groupby(['year', 'week'])['date'].nunique().reset_index()
    
    # Merge complete weeks with actual sessions, filling NaN with 0
    complete_weeks_sessions = complete_weeks[['year', 'week', 'month', 'month_name']].drop_duplicates().merge(
        weekly_sessions, on=['year', 'week'], how='left'
    )
    complete_weeks_sessions['date'] = complete_weeks_sessions['date'].fillna(0)
    
    # Sort by year and week
    complete_weeks_sessions = complete_weeks_sessions.sort_values(['year', 'week'])
    
    # Create a figure and axis with larger size
    fig, ax = plt.subplots(figsize=(24, 12))
    plt.subplots_adjust(left=0.05, right=0.95, top=0.92, bottom=0.08)
    
    # Calculate weeks per row (13 weeks per row = 1 quarter)
    weeks_per_row = 13
    
    # Calculate total rows needed
    total_entries = len(complete_weeks_sessions)
    rows = (total_entries // weeks_per_row) + (1 if total_entries % weeks_per_row else 0)
    
    # Track the current year and month for drawing separators and labels
    current_year = None
    current_month = None
    month_start_x = None
    
    # Plot the weeks
    for idx, row in complete_weeks_sessions.iterrows():
        # Calculate position
        row_idx = idx // weeks_per_row
        col_idx = idx % weeks_per_row
        
        # Check if year has changed
        if current_year != row['year']:
            if current_year is not None:
                # Draw a subtle separator line between years
                y_pos = (rows - row_idx) * 2
                plt.axhline(y=y_pos, color='#666666', linestyle='--', alpha=0.3, linewidth=1)
            current_year = row['year']
        
        # Check if month has changed
        if current_month != row['month']:
            if month_start_x is not None:
                # Add month label for the previous month
                month_width = col_idx - month_start_x
                if month_width > 0:  # Only add label if there's space
                    ax.text(month_start_x + month_width/2, rows * 2 + 0.5,
                           prev_month_name,
                           ha='center', va='bottom',
                           fontsize=10, fontweight='bold',
                           color='#666666')
            month_start_x = col_idx
            current_month = row['month']
            prev_month_name = row['month_name']
        
        # Determine color based on session count
        if row['date'] >= min_sessions:
            color = '#2ecc71'  # Bright green
            alpha = 0.8
        else:
            color = '#e74c3c'  # Red
            alpha = 0.6
        
        # Add block with border
        rect = plt.Rectangle(
            (col_idx * 1.2, (rows - row_idx - 1) * 2),  # Increased spacing
            1, 1.5,  # Wider blocks
            facecolor=color,
            edgecolor='#333333',  # Dark border
            alpha=alpha,
            linewidth=0.5
        )
        ax.add_patch(rect)
        
        # Add week label and count with improved visibility
        week_label = f"Week {row['week']}"
        count_label = f"{int(row['date'])} sessions"
        
        # Add text with better positioning and formatting
        ax.text(col_idx * 1.2 + 0.5, (rows - row_idx - 1) * 2 + 1.1,
                week_label,
                ha='center', va='center',
                color='black', fontsize=9, fontweight='bold')
        
        ax.text(col_idx * 1.2 + 0.5, (rows - row_idx - 1) * 2 + 0.5,
                count_label,
                ha='center', va='center',
                color='black', fontsize=8)
        
        # Add year label at the start of each row with background
        if col_idx == 0:
            # Add background rectangle for year label
            year_rect = plt.Rectangle(
                (-1, (rows - row_idx - 1) * 2),
                0.8, 1.5,
                facecolor='#f8f9fa',
                edgecolor='#dee2e6',
                alpha=0.8,
                linewidth=0.5
            )
            ax.add_patch(year_rect)
            
            ax.text(-0.6, (rows - row_idx - 1) * 2 + 0.75,
                    str(row['year']),
                    ha='center', va='center',
                    fontsize=11, fontweight='bold',
                    bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=2))
    
    # Add the last month label
    if month_start_x is not None:
        ax.text(month_start_x + (col_idx - month_start_x)/2, rows * 2 + 0.5,
               prev_month_name,
               ha='center', va='bottom',
               fontsize=10, fontweight='bold',
               color='#666666')
    
    # Set the axis limits with padding
    ax.set_xlim(-1, weeks_per_row * 1.2)
    ax.set_ylim(-1, rows * 2 + 1)  # Added extra space for month labels
    
    # Remove axis lines and ticks
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Add title with better formatting
    plt.suptitle('Weekly Workout Blocks', y=0.98, fontsize=16, fontweight='bold')
    
    # Add subtitle explaining colors with improved formatting
    plt.title(f'Green: ≥{min_sessions} sessions | Red: <{min_sessions} sessions',
             pad=20, fontsize=14, color='#666666')
    
    # Add legend with clearer labels
    legend_elements = [
        plt.Rectangle((0, 0), 1, 1, facecolor='#2ecc71', alpha=0.8, label=f'≥{min_sessions} sessions'),
        plt.Rectangle((0, 0), 1, 1, facecolor='#e74c3c', alpha=0.6, label=f'<{min_sessions} sessions')
    ]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.0, -0.05),
             fontsize=12, frameon=True)
    
    return fig

# Function to create GitHub-style weekly blocks with hover info
def create_github_style_blocks(workout_data):
    # Get min and max dates
    min_date = workout_data['date'].min()
    max_date = workout_data['date'].max()
    
    # Adjust dates to start from January 1st and end on December 31st of the respective years
    min_date = pd.Timestamp(year=min_date.year, month=1, day=1)
    max_date = pd.Timestamp(year=max_date.year, month=12, day=31)
    
    # Create a complete date range with all weeks
    date_range = pd.date_range(start=min_date, end=max_date, freq='W-MON')  # Start weeks on Monday
    complete_weeks = pd.DataFrame({
        'date_start': date_range,
        'date_end': date_range + pd.Timedelta(days=6),
        'year': date_range.year,
        'week': date_range.isocalendar().week,
        'month': date_range.month,
        'month_name': date_range.strftime('%b')
    })
    
    # Count sessions per week in actual data
    workout_data['week'] = workout_data['date'].dt.isocalendar().week
    workout_data['year'] = workout_data['date'].dt.isocalendar().year
    weekly_sessions = workout_data.groupby(['year', 'week'])['date'].nunique().reset_index()
    
    # Merge complete weeks with actual sessions
    complete_weeks_sessions = complete_weeks.merge(
        weekly_sessions, 
        on=['year', 'week'], 
        how='left'
    )
    complete_weeks_sessions['date'] = complete_weeks_sessions['date'].fillna(0)
    
    # Sort by year and week
    complete_weeks_sessions = complete_weeks_sessions.sort_values(['year', 'week'])
    
    # Define GitHub-style colors
    colors = {
        0: '#ebedf0',    # Gray (0 workouts)
        1: '#9be9a8',    # Light green (1-2 workouts)
        2: '#40c463',    # Medium green (3-5 workouts)
        3: '#216e39'     # Dark green (6-7 workouts)
    }
    
    # Create color and hover text arrays
    color_array = []
    hover_texts = []
    
    # Process data for visualization
    years = sorted(complete_weeks_sessions['year'].unique(), reverse=True)  # Sort years in reverse order
    weeks_data = []
    
    for year in years:
        year_data = complete_weeks_sessions[complete_weeks_sessions['year'] == year]
        
        # Create week blocks
        for _, row in year_data.iterrows():
            sessions = row['date']
            
            # Determine color
            if sessions == 0:
                color = colors[0]
            elif sessions <= 2:
                color = colors[1]
            elif sessions <= 5:
                color = colors[2]
            else:
                color = colors[3]
            
            color_array.append(color)
            
            # Create hover text
            date_range_str = f"{row['date_start'].strftime('%b %d')} - {row['date_end'].strftime('%b %d, %Y')}"
            sessions_str = f"{int(sessions)} session{'s' if sessions != 1 else ''}"
            hover_text = f"Week of {date_range_str}<br>{sessions_str}"
            hover_texts.append(hover_text)
            
            weeks_data.append({
                'x': row['week'],
                'y': year,
                'color': color,
                'hover_text': hover_text,
                'sessions': sessions
            })
    
    # Create the Plotly figure
    fig = go.Figure()
    
    # Add squares for each week
    for week in weeks_data:
        fig.add_trace(go.Scatter(
            x=[week['x']],
            y=[week['y']],
            mode='markers',
            marker=dict(
                size=20,  # Keep size consistent
                color=week['color'],
                symbol='square',
                line=dict(color='white', width=1)
            ),
            text=week['hover_text'],
            hoverinfo='text',
            showlegend=False
        ))
    
    # Update layout with reduced spacing and reversed y-axis
    fig.update_layout(
        title='GitHub-Style Weekly Activity',
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=300,  # Reduced height
        margin=dict(l=50, r=50, t=50, b=50),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            tickmode='array',
            ticktext=list(complete_weeks_sessions['month_name'].unique()),
            tickvals=list(complete_weeks_sessions.groupby('month')['week'].mean()),
            tickangle=0
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            tickmode='array',
            ticktext=list(years),  # Years are already reversed
            tickvals=list(years),
            # Add custom range to control spacing
            range=[max(years) + 0.3, min(years) - 0.3],  # Reversed range for reversed order
            scaleanchor='x',  # This makes the y-axis scale match the x-axis
            scaleratio=1.5,   # This controls the aspect ratio (smaller = more compressed vertically)
            constrain='domain'  # This ensures the scaling is maintained
        )
    )
    
    # Add legend as a separate trace
    for level, color in colors.items():
        label = {
            0: 'No workouts',
            1: '1-2 workouts',
            2: '3-5 workouts',
            3: '6-7 workouts'
        }[level]
        
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(size=10, color=color, symbol='square'),
            name=label,
            showlegend=True
        ))
    
    return fig

# Load and process data
@st.cache_data
def load_data():
    # Read all CSV files
    hevy_df = pd.read_csv('workout_hevy.csv')
    strong_df = pd.read_csv('workout_strong.csv')
    jefit_df = pd.read_csv('workout_log_jeefit.csv')
    
    # Standardize Hevy data
    hevy_df['date'] = pd.to_datetime(hevy_df['start_time'], format='%d %b %Y, %H:%M')
    hevy_df['exercise'] = hevy_df['exercise_title'].apply(standardize_exercise_name)
    hevy_df['weight'] = hevy_df['weight_kg']
    hevy_df['set_number'] = hevy_df['set_index'] + 1
    hevy_df['source'] = 'Hevy'
    
    # Standardize Strong data
    strong_df['date'] = pd.to_datetime(strong_df['Date'])
    strong_df['exercise'] = strong_df['Exercise Name'].apply(standardize_exercise_name)
    strong_df['weight'] = strong_df['Weight']
    strong_df['reps'] = strong_df['Reps']
    strong_df['set_number'] = strong_df['Set Order']
    strong_df['source'] = 'Strong'
    
    # Process Jefit data
    jefit_df['date'] = pd.to_datetime(jefit_df['mydate'])
    jefit_df['exercise'] = jefit_df['ename'].apply(standardize_exercise_name)
    jefit_df['source'] = 'Jefit'
    
    # Expand Jefit sets into separate rows
    jefit_expanded = []
    for _, row in jefit_df.iterrows():
        sets = row['logs'].split(',')
        for i, set_info in enumerate(sets):
            if set_info.strip():
                weight, reps = map(float, set_info.split('x'))
                jefit_expanded.append({
                    'date': row['date'],
                    'exercise': row['exercise'],
                    'weight': weight,
                    'reps': reps,
                    'set_number': i + 1,
                    'source': 'Jefit'
                })
    
    jefit_df = pd.DataFrame(jefit_expanded)
    
    # Select common columns
    common_columns = ['date', 'exercise', 'weight', 'reps', 'set_number', 'source']
    hevy_df = hevy_df[common_columns]
    strong_df = strong_df[common_columns]
    jefit_df = jefit_df[common_columns]
    
    # Combine all datasets
    combined_df = pd.concat([hevy_df, strong_df, jefit_df], ignore_index=True)
    
    # Calculate 1RM for each set
    combined_df['one_rm'] = combined_df.apply(lambda x: calculate_1rm(x['weight'], x['reps']), axis=1)
    
    # Sort by date
    combined_df = combined_df.sort_values('date')
    
    return combined_df, hevy_df, strong_df, jefit_df

# Load data
combined_df, hevy_df, strong_df, jefit_df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(combined_df['date'].min(), combined_df['date'].max()),
    min_value=combined_df['date'].min().date(),
    max_value=combined_df['date'].max().date()
)

app_filter = st.sidebar.multiselect(
    "Select App",
    options=['Hevy', 'Strong', 'Jefit'],
    default=['Hevy', 'Strong', 'Jefit']
)

# Filter data based on sidebar selections
filtered_df = combined_df[
    (combined_df['date'].dt.date >= date_range[0]) &
    (combined_df['date'].dt.date <= date_range[1]) &
    (combined_df['source'].isin(app_filter))
]

# Overview Statistics
st.header("Overview Statistics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Workouts", len(filtered_df.groupby('date').first()))
with col2:
    st.metric("Unique Exercises", filtered_df['exercise'].nunique())
with col3:
    st.metric("Average Sets per Workout", round(filtered_df.groupby('date')['set_number'].max().mean(), 1))
with col4:
    st.metric("Total Workout Days", filtered_df['date'].nunique())

# Calendar View
st.header("Workout Calendar")
calendar_year = st.slider("Select Year", 
                         min_value=filtered_df['date'].dt.year.min(),
                         max_value=filtered_df['date'].dt.year.max(),
                         value=filtered_df['date'].dt.year.max())

# Get unique workout dates for the selected year
workout_dates = filtered_df[filtered_df['date'].dt.year == calendar_year]['date'].unique()

# Create and display the calendar
calendar_fig = create_calendar_heatmap(workout_dates, calendar_year)
st.pyplot(calendar_fig)

# Weekly Blocks View
st.header("Weekly Workout Blocks")
min_sessions = st.slider("Minimum Sessions for Green Highlight", 
                        min_value=1, 
                        max_value=7, 
                        value=3)

# Create and display the weekly blocks
weekly_blocks_fig = create_weekly_blocks(filtered_df, min_sessions)
st.pyplot(weekly_blocks_fig)

# GitHub-Style Weekly Activity
st.header("GitHub-Style Weekly Activity")
github_blocks_fig = create_github_style_blocks(filtered_df)
st.plotly_chart(github_blocks_fig, use_container_width=True)

# Workout Frequency Over Time
st.header("Workout Frequency")

# Create two columns for the graphs
col1, col2 = st.columns(2)

with col1:
    # Monthly view
    filtered_df['month_year'] = filtered_df['date'].dt.to_period('M')
    monthly_workouts = filtered_df.groupby('month_year')['date'].nunique().reset_index()
    monthly_workouts['month_year'] = monthly_workouts['month_year'].astype(str)

    fig_monthly = px.line(monthly_workouts, x='month_year', y='date',
                         title='Monthly Workout Frequency',
                         labels={'date': 'Number of Workouts', 'month_year': 'Month'})
    fig_monthly.update_xaxes(tickangle=45)
    st.plotly_chart(fig_monthly, use_container_width=True)

with col2:
    # Weekly view
    filtered_df['week_start'] = filtered_df['date'].dt.to_period('W').astype(str).str.split('/').str[0]
    weekly_workouts = filtered_df.groupby('week_start')['date'].nunique().reset_index()
    
    fig_weekly = px.bar(weekly_workouts, x='week_start', y='date',
                       title='Weekly Workout Frequency',
                       labels={'date': 'Number of Workouts', 'week_start': 'Week Starting'})
    fig_weekly.update_xaxes(tickangle=45)
    st.plotly_chart(fig_weekly, use_container_width=True)

# Exercise Distribution
st.header("Exercise Distribution")
exercise_counts = filtered_df['exercise'].value_counts().head(10)
fig_exercises = px.bar(x=exercise_counts.index, y=exercise_counts.values,
                      title='Top 10 Most Performed Exercises',
                      labels={'x': 'Exercise', 'y': 'Number of Sets'})
st.plotly_chart(fig_exercises, use_container_width=True)

# Exercise Analysis Section
st.header("Exercise Analysis")
selected_exercise = st.selectbox("Select Exercise", 
                               options=filtered_df['exercise'].unique(),
                               key="exercise_selector")

# Create two columns for the exercise analysis
col1, col2 = st.columns(2)

with col1:
    # Top 10 Sets
    st.subheader("Top 10 Sets")
    top_sets = filtered_df[filtered_df['exercise'] == selected_exercise].nlargest(10, 'one_rm')
    top_sets['date'] = top_sets['date'].dt.strftime('%Y-%m-%d')
    top_sets_display = top_sets[['date', 'weight', 'reps', 'one_rm', 'source']].copy()
    top_sets_display.columns = ['Date', 'Weight (kg)', 'Reps', '1RM (kg)', 'App']
    top_sets_display = top_sets_display.sort_values('1RM (kg)', ascending=False)
    st.dataframe(top_sets_display)

with col2:
    # Weight and 1RM Progression
    st.subheader("Weight and 1RM Progression")
    exercise_progression = filtered_df[filtered_df['exercise'] == selected_exercise].groupby('date').agg({
        'weight': 'max',
        'one_rm': 'max'
    }).reset_index()

    # Create figure with secondary y-axis
    fig_progression = go.Figure()

    # Add traces
    fig_progression.add_trace(
        go.Scatter(x=exercise_progression['date'], y=exercise_progression['weight'],
                   name="Working Weight",
                   line=dict(color='blue'))
    )

    fig_progression.add_trace(
        go.Scatter(x=exercise_progression['date'], y=exercise_progression['one_rm'],
                   name="Estimated 1RM",
                   line=dict(color='red'))
    )

    # Update layout
    fig_progression.update_layout(
        title=f'Weight and 1RM Progression',
        xaxis_title="Date",
        yaxis_title="Weight (kg)",
        yaxis2=dict(
            title="1RM (kg)",
            overlaying="y",
            side="right"
        )
    )

    st.plotly_chart(fig_progression, use_container_width=True)

# Volume Analysis
st.header("Volume Analysis")
volume_data = filtered_df.groupby('date').agg({
    'weight': lambda x: (x * filtered_df.loc[x.index, 'reps']).sum(),
    'exercise': 'count'
}).reset_index()

fig_volume = px.scatter(volume_data, x='date', y='weight',
                       size='exercise',
                       title='Daily Volume (Weight × Reps)',
                       labels={'weight': 'Total Volume (kg)', 'exercise': 'Number of Exercises'})
st.plotly_chart(fig_volume, use_container_width=True)

# Detailed Exercise Data
st.header("Detailed Exercise Data")
exercise_details = filtered_df.groupby('exercise').agg({
    'weight': ['max', 'mean'],
    'reps': ['max', 'mean'],
    'one_rm': ['max', 'mean'],
    'date': 'count'
}).reset_index()

exercise_details.columns = ['Exercise', 'Max Weight', 'Avg Weight', 'Max Reps', 'Avg Reps', 
                          'Max 1RM', 'Avg 1RM', 'Total Sets']
exercise_details = exercise_details.sort_values('Max 1RM', ascending=False)
st.dataframe(exercise_details)

# App Comparison
st.header("App Comparison")
app_stats = filtered_df.groupby('source').agg({
    'exercise': 'count',
    'weight': lambda x: (x * filtered_df.loc[x.index, 'reps']).sum(),
    'one_rm': 'max',
    'date': 'nunique'
}).reset_index()

app_stats.columns = ['App', 'Total Sets', 'Total Volume', 'Max 1RM', 'Workout Days']
st.dataframe(app_stats) 