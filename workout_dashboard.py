import streamlit as st

# Import our modules
from models.data_processor import DataProcessor
from models.workout_analyzer import WorkoutAnalyzer
from visualizations.calendar_view import CalendarVisualizer
from visualizations.progression_charts import ProgressionVisualizer
from visualizations.workout_blocks import WorkoutBlocksVisualizer

# Set page config
st.set_page_config(page_title="Workout Dashboard", layout="wide")


#######################
# Main Dashboard Class
#######################


class WorkoutDashboard:
    def __init__(self):
        # Initialize data processor
        self.data_processor = DataProcessor()

        # Load data
        self.combined_df, self.hevy_df, self.strong_df, self.jefit_df = self.data_processor.load_data()

        # Initialize analyzers and visualizers
        self.analyzer = WorkoutAnalyzer(self.combined_df)
        self.calendar_viz = CalendarVisualizer()
        self.blocks_viz = WorkoutBlocksVisualizer()
        self.progression_viz = ProgressionVisualizer()

        # Initialize filtered dataframe
        self.filtered_df = self.combined_df

    def setup_sidebar_filters(self):
        """Setup sidebar filters and apply them to the data"""
        st.sidebar.header("Filters")

        # Date range filter
        date_range = st.sidebar.date_input("Select Date Range",
                                           value=(self.combined_df['date'].min(), self.combined_df['date'].max()),
                                           min_value=self.combined_df['date'].min().date(),
                                           max_value=self.combined_df['date'].max().date())

        # App filter
        app_filter = st.sidebar.multiselect("Select App", options=['Hevy', 'Strong', 'Jefit'],
                                            default=['Hevy', 'Strong', 'Jefit'])

        # Apply filters
        self.filtered_df = self.combined_df[(self.combined_df['date'].dt.date >= date_range[0]) & (
                self.combined_df['date'].dt.date <= date_range[1]) & (self.combined_df['source'].isin(app_filter))]

        return date_range, app_filter

    def display_overview_statistics(self):
        """Display overview statistics section"""
        st.header("Overview Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Workouts", len(self.filtered_df.groupby('date').first()))
        with col2:
            st.metric("Unique Exercises", self.filtered_df['exercise'].nunique())
        with col3:
            st.metric("Average Sets per Workout", round(self.filtered_df.groupby('date')['set_number'].max().mean(), 1))
        with col4:
            st.metric("Total Workout Days", self.filtered_df['date'].nunique())

    def display_calendar_view(self):
        """Display calendar view section"""
        st.header("Workout Calendar")
        calendar_year = st.slider("Select Year", min_value=self.filtered_df['date'].dt.year.min(),
                                  max_value=self.filtered_df['date'].dt.year.max(),
                                  value=self.filtered_df['date'].dt.year.max())

        # Get unique workout dates for the selected year
        workout_dates = self.filtered_df[self.filtered_df['date'].dt.year == calendar_year]['date'].unique()

        # Create and display the calendar
        calendar_fig = self.calendar_viz.create_calendar_heatmap(workout_dates, calendar_year)
        st.pyplot(calendar_fig)

    def display_weekly_blocks(self):
        """Display weekly blocks section"""
        st.header("Weekly Workout Blocks")
        min_sessions = st.slider("Minimum Sessions for Green Highlight", min_value=1, max_value=7, value=3)

        # Create and display the weekly blocks
        weekly_blocks_fig = self.blocks_viz.create_weekly_blocks(self.filtered_df, min_sessions)
        st.pyplot(weekly_blocks_fig)

        # GitHub-Style Weekly Activity
        st.header("GitHub-Style Weekly Activity")
        github_blocks_fig = self.blocks_viz.create_github_style_blocks(self.filtered_df)
        st.plotly_chart(github_blocks_fig, use_container_width=True)

    def display_workout_frequency(self):
        """Display workout frequency section"""
        st.header("Workout Frequency")

        # Create two columns for the graphs
        col1, col2 = st.columns(2)

        with col1:
            # Monthly view
            monthly_fig = self.progression_viz.create_monthly_frequency_chart(self.filtered_df)
            st.plotly_chart(monthly_fig, use_container_width=True)

        with col2:
            # Weekly view
            weekly_fig = self.progression_viz.create_weekly_frequency_chart(self.filtered_df)
            st.plotly_chart(weekly_fig, use_container_width=True)

    def display_exercise_distribution(self):
        """Display exercise distribution section"""
        st.header("Exercise Distribution")
        exercise_fig = self.progression_viz.create_exercise_distribution_chart(self.filtered_df)
        st.plotly_chart(exercise_fig, use_container_width=True)

    def display_exercise_analysis(self):
        """Display exercise analysis section"""
        st.header("Exercise Analysis")
        selected_exercise = st.selectbox("Select Exercise", options=self.filtered_df['exercise'].unique(),
                                         key="exercise_selector")

        # Create two columns for the exercise analysis
        col1, col2 = st.columns(2)

        with col1:
            # Top 10 Sets
            st.subheader("Top 10 Sets")
            top_sets_display = self.analyzer.get_top_sets(self.filtered_df, selected_exercise, 10)
            st.dataframe(top_sets_display)

        with col2:
            # Weight and 1RM Progression
            st.subheader("Weight and 1RM Progression")
            progression_fig = self.progression_viz.create_exercise_progression_chart(self.filtered_df,
                                                                                     selected_exercise)
            st.plotly_chart(progression_fig, use_container_width=True)

    def display_volume_analysis(self):
        """Display volume analysis section"""
        st.header("Volume Analysis")
        volume_fig = self.progression_viz.create_volume_chart(self.filtered_df)
        st.plotly_chart(volume_fig, use_container_width=True)

    def display_detailed_exercise_data(self):
        """Display detailed exercise data section"""
        st.header("Detailed Exercise Data")
        exercise_details = self.analyzer.get_exercise_details(self.filtered_df)
        st.dataframe(exercise_details)

    def display_app_comparison(self):
        """Display app comparison section"""
        st.header("App Comparison")
        app_stats = self.analyzer.get_app_comparison(self.filtered_df)
        st.dataframe(app_stats)

    def run(self):
        """Run the dashboard application"""
        # Setup sidebar filters
        self.setup_sidebar_filters()

        # Display all sections
        self.display_overview_statistics()
        self.display_calendar_view()
        self.display_weekly_blocks()
        self.display_workout_frequency()
        self.display_exercise_distribution()
        self.display_exercise_analysis()
        self.display_volume_analysis()
        self.display_detailed_exercise_data()
        self.display_app_comparison()


# Run the dashboard
if __name__ == "__main__":
    dashboard = WorkoutDashboard()
    dashboard.run()
