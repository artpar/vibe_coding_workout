import pandas as pd
import os
import shutil
from datetime import datetime

from utils.calculations import standardize_exercise_name, calculate_1rm


#######################
# Data Processing
#######################

class DataProcessor:
    """Class for loading and processing workout data"""
    
    def __init__(self):
        """Initialize the data processor with data directories"""
        self.data_dir = "data"
        self.uploads_dir = os.path.join(self.data_dir, "uploads")
        self.ensure_data_directories()
        
    def ensure_data_directories(self):
        """Ensure data directories exist"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.uploads_dir, exist_ok=True)
        
    def save_uploaded_file(self, uploaded_file):
        """Save an uploaded file to the uploads directory"""
        # Create a timestamped filename to avoid overwriting
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = os.path.splitext(uploaded_file.name)[1]
        source_type = self._detect_source_type(uploaded_file)
        
        if not source_type:
            return None, "Could not determine the workout data source type"
        
        # Create a filename with timestamp and source type
        new_filename = f"{source_type}_{timestamp}{file_ext}"
        file_path = os.path.join(self.uploads_dir, new_filename)
        
        # Save the file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        return file_path, f"File saved as {new_filename}"
    
    def _detect_source_type(self, uploaded_file):
        """Detect the source type (Hevy, Strong, Jefit) from the uploaded file"""
        # Read a small sample to detect the format
        try:
            # Reset the file pointer to the beginning
            uploaded_file.seek(0)
            sample_df = pd.read_csv(uploaded_file, nrows=5)
            uploaded_file.seek(0)  # Reset again for future use
            
            # Check for column patterns to identify the source
            if 'exercise_title' in sample_df.columns:
                return 'hevy'
            elif 'Exercise Name' in sample_df.columns:
                return 'strong'
            elif 'ename' in sample_df.columns and 'logs' in sample_df.columns:
                return 'jefit'
            else:
                return None
        except Exception:
            return None

    def load_data(self):
        """Load and process data from CSV files"""
        # Default file paths
        default_files = {
            'hevy': 'workout_hevy.csv',
            'strong': 'workout_strong.csv',
            'jefit': 'workout_log_jeefit.csv'
        }
        
        # Lists to hold dataframes from each source
        hevy_dfs = []
        strong_dfs = []
        jefit_dfs = []
        
        # Load default files if they exist
        if os.path.exists(default_files['hevy']):
            hevy_dfs.append(pd.read_csv(default_files['hevy']))
        if os.path.exists(default_files['strong']):
            strong_dfs.append(pd.read_csv(default_files['strong']))
        if os.path.exists(default_files['jefit']):
            jefit_dfs.append(pd.read_csv(default_files['jefit']))
        
        # Load any uploaded files
        if os.path.exists(self.uploads_dir):
            for filename in os.listdir(self.uploads_dir):
                file_path = os.path.join(self.uploads_dir, filename)
                if filename.startswith('hevy_'):
                    hevy_dfs.append(pd.read_csv(file_path))
                elif filename.startswith('strong_'):
                    strong_dfs.append(pd.read_csv(file_path))
                elif filename.startswith('jefit_'):
                    jefit_dfs.append(pd.read_csv(file_path))
        
        # Combine files from the same source
        hevy_df = pd.concat(hevy_dfs) if hevy_dfs else pd.DataFrame()
        strong_df = pd.concat(strong_dfs) if strong_dfs else pd.DataFrame()
        jefit_df = pd.concat(jefit_dfs) if jefit_dfs else pd.DataFrame()
        
        # Process only if we have data
        if not hevy_df.empty:
            # Standardize Hevy data
            hevy_df['date'] = pd.to_datetime(hevy_df['start_time'], format='%d %b %Y, %H:%M')
            hevy_df['exercise'] = hevy_df['exercise_title'].apply(standardize_exercise_name)
            hevy_df['weight'] = hevy_df['weight_kg']
            hevy_df['set_number'] = hevy_df['set_index'] + 1
            hevy_df['source'] = 'Hevy'
        
        if not strong_df.empty:
            # Standardize Strong data
            strong_df['date'] = pd.to_datetime(strong_df['Date'])
            strong_df['exercise'] = strong_df['Exercise Name'].apply(standardize_exercise_name)
            strong_df['weight'] = strong_df['Weight']
            strong_df['reps'] = strong_df['Reps']
            strong_df['set_number'] = strong_df['Set Order']
            strong_df['source'] = 'Strong'
        
        if not jefit_df.empty:
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
            
            jefit_df = pd.DataFrame(jefit_expanded) if jefit_expanded else pd.DataFrame()
        
        # Select common columns and combine all datasets
        common_columns = ['date', 'exercise', 'weight', 'reps', 'set_number', 'source']
        dfs_to_combine = []
        
        if not hevy_df.empty:
            dfs_to_combine.append(hevy_df[common_columns])
        if not strong_df.empty:
            dfs_to_combine.append(strong_df[common_columns])
        if not jefit_df.empty:
            dfs_to_combine.append(jefit_df[common_columns])
        
        # Combine all datasets
        combined_df = pd.concat(dfs_to_combine, ignore_index=True) if dfs_to_combine else pd.DataFrame(columns=common_columns)
        
        if not combined_df.empty:
            # Calculate 1RM for each set
            combined_df['one_rm'] = combined_df.apply(lambda x: calculate_1rm(x['weight'], x['reps']), axis=1)
            
            # Sort by date
            combined_df = combined_df.sort_values('date')
        
        return combined_df, hevy_df, strong_df, jefit_df
