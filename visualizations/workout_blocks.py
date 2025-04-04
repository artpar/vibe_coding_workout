import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go


class WorkoutBlocksVisualizer:
    """Class for creating workout block visualizations"""

    def create_weekly_blocks(self, workout_data, min_sessions=3):
        """Create weekly blocks visualization"""
        # Get min and max dates
        min_date = workout_data['date'].min()
        max_date = workout_data['date'].max()

        # Create a complete date range with all weeks
        date_range = pd.date_range(start=min_date, end=max_date, freq='W')
        complete_weeks = pd.DataFrame(
            {'date': date_range, 'year': date_range.year, 'week': date_range.isocalendar().week,
                'month': date_range.month, 'month_name': date_range.strftime('%b')  # Short month name
            })

        # Count sessions per week in actual data
        workout_data['week'] = workout_data['date'].dt.isocalendar().week
        workout_data['year'] = workout_data['date'].dt.isocalendar().year
        weekly_sessions = workout_data.groupby(['year', 'week'])['date'].nunique().reset_index()

        # Merge complete weeks with actual sessions, filling NaN with 0
        complete_weeks_sessions = complete_weeks[['year', 'week', 'month', 'month_name']].drop_duplicates().merge(
            weekly_sessions, on=['year', 'week'], how='left')
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
                        ax.text(month_start_x + month_width / 2, rows * 2 + 0.5, prev_month_name, ha='center',
                                va='bottom', fontsize=10, fontweight='bold', color='#666666')
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
            rect = plt.Rectangle((col_idx * 1.2, (rows - row_idx - 1) * 2),  # Increased spacing
                1, 1.5,  # Wider blocks
                facecolor=color, edgecolor='#333333',  # Dark border
                alpha=alpha, linewidth=0.5)
            ax.add_patch(rect)

            # Add week label and count with improved visibility
            week_label = f"Week {row['week']}"
            count_label = f"{int(row['date'])} sessions"

            # Add text with better positioning and formatting
            ax.text(col_idx * 1.2 + 0.5, (rows - row_idx - 1) * 2 + 1.1, week_label, ha='center', va='center',
                    color='black', fontsize=9, fontweight='bold')

            ax.text(col_idx * 1.2 + 0.5, (rows - row_idx - 1) * 2 + 0.5, count_label, ha='center', va='center',
                    color='black', fontsize=8)

            # Add year label at the start of each row with background
            if col_idx == 0:
                # Add background rectangle for year label
                year_rect = plt.Rectangle((-1, (rows - row_idx - 1) * 2), 0.8, 1.5, facecolor='#f8f9fa',
                    edgecolor='#dee2e6', alpha=0.8, linewidth=0.5)
                ax.add_patch(year_rect)

                ax.text(-0.6, (rows - row_idx - 1) * 2 + 0.75, str(row['year']), ha='center', va='center', fontsize=11,
                        fontweight='bold', bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=2))

        # Add the last month label
        if month_start_x is not None:
            ax.text(month_start_x + (col_idx - month_start_x) / 2, rows * 2 + 0.5, prev_month_name, ha='center',
                    va='bottom', fontsize=10, fontweight='bold', color='#666666')

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
        plt.title(f'Green: ≥{min_sessions} sessions | Red: <{min_sessions} sessions', pad=20, fontsize=14,
                  color='#666666')

        # Add legend with clearer labels
        legend_elements = [
            plt.Rectangle((0, 0), 1, 1, facecolor='#2ecc71', alpha=0.8, label=f'≥{min_sessions} sessions'),
            plt.Rectangle((0, 0), 1, 1, facecolor='#e74c3c', alpha=0.6, label=f'<{min_sessions} sessions')]
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.0, -0.05), fontsize=12, frameon=True)

        return fig

    def create_github_style_blocks(self, workout_data):
        """Create GitHub-style weekly blocks with hover info"""
        # Get min and max dates
        min_date = workout_data['date'].min()
        max_date = workout_data['date'].max()

        # Adjust dates to start from January 1st and end on December 31st of the respective years
        min_date = pd.Timestamp(year=min_date.year, month=1, day=1)
        max_date = pd.Timestamp(year=max_date.year, month=12, day=31)

        # Create a complete date range with all weeks
        date_range = pd.date_range(start=min_date, end=max_date, freq='W-MON')  # Start weeks on Monday
        complete_weeks = pd.DataFrame(
            {'date_start': date_range, 'date_end': date_range + pd.Timedelta(days=6), 'year': date_range.year,
                'week': date_range.isocalendar().week, 'month': date_range.month,
                'month_name': date_range.strftime('%b')})

        # Count sessions per week in actual data
        workout_data['week'] = workout_data['date'].dt.isocalendar().week
        workout_data['year'] = workout_data['date'].dt.isocalendar().year
        weekly_sessions = workout_data.groupby(['year', 'week'])['date'].nunique().reset_index()

        # Merge complete weeks with actual sessions
        complete_weeks_sessions = complete_weeks.merge(weekly_sessions, on=['year', 'week'], how='left')
        complete_weeks_sessions['date'] = complete_weeks_sessions['date'].fillna(0)

        # Sort by year and week
        complete_weeks_sessions = complete_weeks_sessions.sort_values(['year', 'week'])

        # Define GitHub-style colors
        colors = {0: '#ebedf0',  # Gray (0 workouts)
            1: '#9be9a8',  # Light green (1-2 workouts)
            2: '#40c463',  # Medium green (3-5 workouts)
            3: '#216e39'  # Dark green (6-7 workouts)
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

                weeks_data.append(
                    {'x': row['week'], 'y': year, 'color': color, 'hover_text': hover_text, 'sessions': sessions})

        # Create the Plotly figure
        fig = go.Figure()

        # Add squares for each week
        for week in weeks_data:
            fig.add_trace(
                go.Scatter(x=[week['x']], y=[week['y']], mode='markers', marker=dict(size=20,  # Keep size consistent
                    color=week['color'], symbol='square', line=dict(color='white', width=1)), text=week['hover_text'],
                    hoverinfo='text', showlegend=False))

        # Update layout with reduced spacing and reversed y-axis
        fig.update_layout(title='GitHub-Style Weekly Activity', plot_bgcolor='white', paper_bgcolor='white', height=300,
            # Reduced height
            margin=dict(l=50, r=50, t=50, b=50), xaxis=dict(showgrid=False, zeroline=False, tickmode='array',
                ticktext=list(complete_weeks_sessions['month_name'].unique()),
                tickvals=list(complete_weeks_sessions.groupby('month')['week'].mean()), tickangle=0),
            yaxis=dict(showgrid=False, zeroline=False, tickmode='array', ticktext=list(years),
                # Years are already reversed
                tickvals=list(years), # Add custom range to control spacing
                range=[max(years) + 0.3, min(years) - 0.3],  # Reversed range for reversed order
                scaleanchor='x',  # This makes the y-axis scale match the x-axis
                scaleratio=1.5,  # This controls the aspect ratio (smaller = more compressed vertically)
                constrain='domain'  # This ensures the scaling is maintained
            ))

        # Add legend as a separate trace
        for level, color in colors.items():
            label = {0: 'No workouts', 1: '1-2 workouts', 2: '3-5 workouts', 3: '6-7 workouts'}[level]

            fig.add_trace(
                go.Scatter(x=[None], y=[None], mode='markers', marker=dict(size=10, color=color, symbol='square'),
                    name=label, showlegend=True))

        return fig
