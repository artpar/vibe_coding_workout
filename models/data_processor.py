import pandas as pd

from utils.calculations import standardize_exercise_name, calculate_1rm


#######################
# Data Processing
#######################

class DataProcessor:
    """Class for loading and processing workout data"""

    def load_data(self):
        """Load and process data from CSV files"""
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
                    jefit_expanded.append(
                        {'date': row['date'], 'exercise': row['exercise'], 'weight': weight, 'reps': reps,
                            'set_number': i + 1, 'source': 'Jefit'})

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
