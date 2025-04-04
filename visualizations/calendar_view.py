#######################
# Visualization Classes
#######################
from datetime import datetime, timedelta

import matplotlib.pyplot as plt


class CalendarVisualizer:
    """Class for creating calendar visualizations"""

    def create_calendar_heatmap(self, workout_dates, year=None):
        """Create a GitHub-style calendar heatmap"""
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
                  '#9be9a8',  # 1-2 contributions
                  '#40c463',  # 3-4 contributions
                  '#30a14e',  # 5-6 contributions
                  '#216e39']  # 7+ contributions

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
                rect = plt.Rectangle((week_num, 6 - day_num),  # Flip y-axis to match GitHub (Monday at top)
                    0.9,  # Width slightly less than 1 for spacing
                    0.9,  # Height slightly less than 1 for spacing
                    facecolor=color, edgecolor='white', linewidth=1)
                ax.add_patch(rect)

                # Add month label at the top of the first full week of each month
                if date.day <= 7 and day_num == 6:  # Saturday of first week
                    ax.text(week_num, 7.5, date.strftime('%b'), ha='center', va='bottom', fontsize=10,
                            fontweight='bold', color='#666666')

            current_date += timedelta(days=7)
            week_num += 1

        # Add weekday labels on the left
        weekdays = ['Mon', 'Wed', 'Fri']
        weekday_positions = [5, 3, 1]  # Corresponding to Monday, Wednesday, Friday
        for day, pos in zip(weekdays, weekday_positions):
            ax.text(-0.5, pos, day, ha='right', va='center', fontsize=10, color='#666666')

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
        legend_elements = [plt.Rectangle((0, 0), 1, 1, facecolor=colors[0], label='No workouts'),
            plt.Rectangle((0, 0), 1, 1, facecolor=colors[1], label='1-2 workouts'),
            plt.Rectangle((0, 0), 1, 1, facecolor=colors[2], label='3-4 workouts'),
            plt.Rectangle((0, 0), 1, 1, facecolor=colors[3], label='5-6 workouts'),
            plt.Rectangle((0, 0), 1, 1, facecolor=colors[4], label='7+ workouts')]
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.0, -0.1), ncol=5, frameon=False,
                  fontsize=10)

        return fig
