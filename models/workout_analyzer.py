#######################
# Workout Analysis
#######################

class WorkoutAnalyzer:
    """Class for analyzing workout data"""
    
    def __init__(self, df=None):
        """Initialize the WorkoutAnalyzer with optional DataFrame
        
        Args:
            df: Pandas DataFrame containing workout data
        """
        self.df = df
    
    def get_top_sets(self, df, exercise, limit=10):
        """Get top sets for a specific exercise"""
        top_sets = df[df['exercise'] == exercise].nlargest(limit, 'one_rm')
        top_sets['date'] = top_sets['date'].dt.strftime('%Y-%m-%d')
        top_sets_display = top_sets[['date', 'weight', 'reps', 'one_rm', 'source']].copy()
        top_sets_display.columns = ['Date', 'Weight (kg)', 'Reps', '1RM (kg)', 'App']
        top_sets_display = top_sets_display.sort_values('1RM (kg)', ascending=False)
        return top_sets_display
    
    def get_exercise_details(self, df):
        """Get detailed exercise statistics"""
        exercise_details = df.groupby('exercise').agg({
            'weight': ['max', 'mean'],
            'reps': ['max', 'mean'],
            'one_rm': ['max', 'mean'],
            'date': 'count'
        }).reset_index()
        
        exercise_details.columns = ['Exercise', 'Max Weight', 'Avg Weight', 'Max Reps', 'Avg Reps', 
                                  'Max 1RM', 'Avg 1RM', 'Total Sets']
        exercise_details = exercise_details.sort_values('Max 1RM', ascending=False)
        return exercise_details
    
    def get_app_comparison(self, df):
        """Get app comparison statistics"""
        app_stats = df.groupby('source').agg({
            'exercise': 'count',
            'weight': lambda x: (x * df.loc[x.index, 'reps']).sum(),
            'one_rm': 'max',
            'date': 'nunique'
        }).reset_index()
        
        app_stats.columns = ['App', 'Total Sets', 'Total Volume', 'Max 1RM', 'Workout Days']
        return app_stats
