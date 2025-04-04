import streamlit as st
import datetime

# Import our modules
from models.data_processor import DataProcessor
from models.workout_analyzer import WorkoutAnalyzer
from visualizations.calendar_view import CalendarVisualizer
from visualizations.progression_charts import ProgressionVisualizer
from visualizations.workout_blocks import WorkoutBlocksVisualizer

# Set page config with wider layout and custom icon
st.set_page_config(
    page_title="Vibe Workout Tracker", 
    page_icon="💪", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
def load_css():
    st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #FF4B2B;
        --secondary-color: #29323c;
        --accent-color: #3498db;
        --text-color: #333;
        --light-bg: #f8f9fa;
        --dark-bg: #1E1E1E;
    }
    
    /* General styling */
    .main {
        background-color: var(--light-bg);
        color: var(--text-color);
    }
    
    h1, h2, h3 {
        color: var(--primary-color);
        font-weight: 700 !important;
    }
    
    /* Card styling */
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary-color);
    }
    
    .metric-label {
        font-size: 1rem;
        color: var(--secondary-color);
        margin-top: 0.5rem;
    }
    
    /* Improved Tab styling */
    .stTabs {
        margin-top: 2rem;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        margin-bottom: 1rem;
        border-bottom: 1px solid #e0e0e0;
        padding-bottom: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: white;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 500;
        font-size: 1rem;
        border: 1px solid #e0e0e0;
        border-bottom: none;
        margin-right: 4px;
        transition: all 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color);
        color: white;
        border-color: var(--primary-color);
        padding-bottom: 12px;
        margin-bottom: -1px;
    }
    
    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
        background-color: #f5f5f5;
        border-color: #d0d0d0;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        padding: 1rem 0.5rem;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: var(--secondary-color);
    }
    
    /* Custom button */
    .custom-button {
        background-color: var(--primary-color);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        text-align: center;
        margin: 1rem 0;
        cursor: pointer;
        font-weight: 600;
    }
    
    /* Motivational quote styling */
    .quote-container {
        background-color: var(--secondary-color);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-style: italic;
    }
    
    /* Progress bar */
    .progress-container {
        margin: 1rem 0;
    }
    
    .progress-label {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
    }
    
    .progress-bar {
        height: 10px;
        background-color: #e0e0e0;
        border-radius: 5px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background-color: var(--primary-color);
        border-radius: 5px;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .metric-value {
            font-size: 1.8rem;
        }
        .metric-label {
            font-size: 0.8rem;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 12px;
            font-size: 0.9rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)


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
        
        # Motivational quotes
        self.quotes = [
            "The only bad workout is the one that didn't happen.",
            "Your body can stand almost anything. It's your mind that you have to convince.",
            "The pain you feel today will be the strength you feel tomorrow.",
            "Fitness is not about being better than someone else. It's about being better than you used to be.",
            "The hardest lift of all is lifting your butt off the couch.",
            "You don't have to be extreme, just consistent.",
            "No matter how slow you go, you're still lapping everyone on the couch.",
            "Strength does not come from the physical capacity. It comes from an indomitable will.",
            "The only place where success comes before work is in the dictionary.",
            "Don't wish for it, work for it."
        ]

    def render_sidebar(self):
        """Render the sidebar with filters and controls"""
        st.sidebar.title("Vibe Workout Tracker 💪")
        
        # Add file upload section
        st.sidebar.header("Upload Workout Data")
        with st.sidebar.expander("Upload New Data", expanded=False):
            uploaded_file = st.file_uploader("Upload workout data (CSV)", type=['csv'])
            
            if uploaded_file is not None:
                if st.button("Process Uploaded File"):
                    with st.spinner("Processing uploaded file..."):
                        # Save the file and get the path
                        file_path, message = self.data_processor.save_uploaded_file(uploaded_file)
                        
                        if file_path:
                            st.success(f"File uploaded successfully! {message}")
                            st.info("Refreshing data... please wait.")
                            # Reload data to include the new file
                            self.combined_df, self.hevy_df, self.strong_df, self.jefit_df = self.data_processor.load_data()
                            # Update the analyzer with new data
                            self.analyzer = WorkoutAnalyzer(self.combined_df)
                            # Update filtered dataframe
                            self.filtered_df = self.combined_df.copy()
                            st.success("Data refreshed with new uploads!")
                        else:
                            st.error(f"Error processing file: {message}")
            
            st.markdown("""
            ### Supported Formats
            - **Hevy** export CSV
            - **Strong** export CSV
            - **Jefit** export CSV
            
            The system will automatically detect the format based on the file structure.
            """)

        # Date range filter with better UI
        min_date = self.combined_df['date'].min().date()
        max_date = self.combined_df['date'].max().date()
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
        with col2:
            end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
        
        date_range = (start_date, end_date)

        # App filter with icons
        st.sidebar.markdown("### 📱 Select Apps")
        hevy = st.sidebar.checkbox("Hevy", value=True)
        strong = st.sidebar.checkbox("Strong", value=True)
        jefit = st.sidebar.checkbox("Jefit", value=True)
        
        app_filter = []
        if hevy:
            app_filter.append('Hevy')
        if strong:
            app_filter.append('Strong')
        if jefit:
            app_filter.append('Jefit')
            
        if not app_filter:  # If nothing selected, select all
            app_filter = ['Hevy', 'Strong', 'Jefit']

        # Apply filters
        self.filtered_df = self.combined_df[(self.combined_df['date'].dt.date >= date_range[0]) & 
                                           (self.combined_df['date'].dt.date <= date_range[1]) & 
                                           (self.combined_df['source'].isin(app_filter))]
        
        # Show a random motivational quote
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 💪 Daily Motivation")
        import random
        quote = random.choice(self.quotes)
        st.sidebar.markdown(f"""
        <div class="quote-container">
            "{quote}"
        </div>
        """, unsafe_allow_html=True)
        
        # Add workout streak calculation
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔥 Your Workout Streak")
        
        # Calculate current streak
        workout_dates = sorted(self.combined_df['date'].dt.date.unique())
        
        if workout_dates:
            today = datetime.datetime.now().date()
            current_streak = 0
            
            # Check if worked out today
            if today in workout_dates:
                current_streak = 1
                check_date = today - datetime.timedelta(days=1)
            else:
                check_date = today
                
            # Count backwards until streak breaks
            while check_date in workout_dates:
                if current_streak > 0 or check_date == today:  # Only increment if already started or today
                    current_streak += 1
                check_date -= datetime.timedelta(days=1)
                
            # Calculate max streak
            max_streak = 1
            current_max = 1
            
            for i in range(1, len(workout_dates)):
                if (workout_dates[i] - workout_dates[i-1]).days == 1:
                    current_max += 1
                else:
                    current_max = 1
                max_streak = max(max_streak, current_max)
                
            # Display streak info
            st.sidebar.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{current_streak}</div>
                <div class="metric-label">Current Streak</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Progress toward max streak
            progress_percent = min(100, (current_streak / max_streak) * 100) if max_streak > 0 else 0
            
            st.sidebar.markdown(f"""
            <div class="progress-container">
                <div class="progress-label">
                    <span>Progress to Max</span>
                    <span>{current_streak}/{max_streak}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {progress_percent}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        return date_range, app_filter

    def display_overview_statistics(self):
        """Display overview statistics section"""
        st.markdown("<h1 style='text-align: center;'>Your Workout Dashboard</h1>", unsafe_allow_html=True)
        
        # Check if data is available
        if self.filtered_df.empty:
            st.warning("⚠️ No workout data available for the selected filters. Try adjusting your filter settings.")
            return
            
        # Create metrics with improved styling
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_workouts = len(self.filtered_df.groupby('date').first())
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_workouts}</div>
                <div class="metric-label">Total Workouts</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            unique_exercises = self.filtered_df['exercise'].nunique()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{unique_exercises}</div>
                <div class="metric-label">Unique Exercises</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            avg_sets = round(self.filtered_df.groupby('date')['set_number'].max().mean(), 1)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{avg_sets}</div>
                <div class="metric-label">Avg Sets/Workout</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col4:
            total_days = self.filtered_df['date'].nunique()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_days}</div>
                <div class="metric-label">Workout Days</div>
            </div>
            """, unsafe_allow_html=True)

    def display_calendar_view(self):
        """Display calendar view section"""
        st.markdown("## 📅 Workout Calendar")
        st.markdown("Track your workout consistency throughout the year")
        
        calendar_year = st.slider("Select Year", 
                                 min_value=self.filtered_df['date'].dt.year.min(),
                                 max_value=self.filtered_df['date'].dt.year.max(),
                                 value=self.filtered_df['date'].dt.year.max())

        # Get unique workout dates for the selected year
        workout_dates = self.filtered_df[self.filtered_df['date'].dt.year == calendar_year]['date'].unique()

        # Create and display the calendar
        calendar_fig = self.calendar_viz.create_calendar_heatmap(workout_dates, calendar_year)
        st.pyplot(calendar_fig)

    def display_weekly_blocks(self):
        """Display weekly blocks section"""
        st.markdown("## 🧱 Weekly Workout Blocks")
        st.markdown("Visualize your workout consistency week by week")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            min_sessions = st.slider("Min Sessions for Green", min_value=1, max_value=7, value=3)
        
        with col1:
            st.markdown("### Weekly Overview")
            st.markdown("Green blocks indicate weeks where you hit your target number of workouts")

        # Create and display the weekly blocks
        weekly_blocks_fig = self.blocks_viz.create_weekly_blocks(self.filtered_df, min_sessions)
        st.pyplot(weekly_blocks_fig)

        # GitHub-Style Weekly Activity
        st.markdown("### GitHub-Style Activity")
        st.markdown("Your workout activity displayed similar to GitHub contributions")
        github_blocks_fig = self.blocks_viz.create_github_style_blocks(self.filtered_df)
        st.plotly_chart(github_blocks_fig, use_container_width=True)

    def display_workout_frequency(self):
        """Display workout frequency section"""
        st.markdown("## 📊 Workout Frequency")
        st.markdown("Track how often you're hitting the gym")

        # Create two columns for the graphs
        col1, col2 = st.columns(2)

        with col1:
            # Monthly view
            st.markdown("### Monthly Frequency")
            monthly_fig = self.progression_viz.create_monthly_frequency_chart(self.filtered_df)
            st.plotly_chart(monthly_fig, use_container_width=True)

        with col2:
            # Weekly view
            st.markdown("### Weekly Frequency")
            weekly_fig = self.progression_viz.create_weekly_frequency_chart(self.filtered_df)
            st.plotly_chart(weekly_fig, use_container_width=True)

    def display_exercise_distribution(self):
        """Display exercise distribution section"""
        st.markdown("## 🏋️ Exercise Distribution")
        st.markdown("See which exercises you perform most frequently")
        
        exercise_fig = self.progression_viz.create_exercise_distribution_chart(self.filtered_df)
        st.plotly_chart(exercise_fig, use_container_width=True)

    def display_exercise_analysis(self):
        """Display exercise analysis section"""
        st.markdown("## 💪 Exercise Analysis")
        st.markdown("Dive deep into your performance for specific exercises")
        
        if self.filtered_df.empty or self.filtered_df['exercise'].nunique() == 0:
            st.warning("⚠️ No exercise data available for the selected filters.")
            return
            
        # Add exercise categories for better organization
        exercise_list = sorted(self.filtered_df['exercise'].unique())
        
        # Create a more user-friendly exercise selector
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_exercise = st.selectbox(
                "Select an exercise to analyze:", 
                options=exercise_list,
                key="exercise_selector"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
            exercise_count = self.filtered_df[self.filtered_df['exercise'] == selected_exercise].shape[0]
            st.markdown(f"**{exercise_count}** sets performed")

        # Create two columns for the exercise analysis
        col1, col2 = st.columns(2)

        with col1:
            # Top 10 Sets with improved styling
            st.markdown("### 🏆 Top 10 Sets")
            top_sets_display = self.analyzer.get_top_sets(self.filtered_df, selected_exercise, 10)
            st.dataframe(top_sets_display, use_container_width=True)

        with col2:
            # Weight and 1RM Progression
            st.markdown("### 📈 Weight and 1RM Progression")
            progression_fig = self.progression_viz.create_exercise_progression_chart(self.filtered_df,
                                                                                   selected_exercise)
            st.plotly_chart(progression_fig, use_container_width=True)
            
        # Add exercise tips section
        st.markdown("### 💡 Exercise Tips")
        
        # Basic exercise tips dictionary (could be expanded)
        exercise_tips = {
            "bench press": "Focus on keeping your back arched and feet planted firmly on the ground. Lower the bar to your mid-chest.",
            "squat": "Keep your chest up, back straight, and push through your heels. Go as low as your mobility allows.",
            "deadlift": "Start with the bar over mid-foot, grab the bar, bend knees until shins touch the bar, lift chest and pull.",
            "overhead press": "Keep your core tight and avoid arching your back. Press straight up overhead.",
            "pull up": "Start from a dead hang and pull until your chin is over the bar. Focus on engaging your lats.",
            "barbell row": "Hinge at the hips, keep your back straight, and pull the bar to your lower chest.",
        }
        
        # Display a tip if available for the selected exercise, or a generic tip
        selected_exercise_lower = selected_exercise.lower()
        tip = "No specific tips available for this exercise. Focus on proper form and controlled movements."
        
        for key, value in exercise_tips.items():
            if key in selected_exercise_lower:
                tip = value
                break
                
        st.info(f"**Tip for {selected_exercise}**: {tip}")

    def display_volume_analysis(self):
        """Display volume analysis section"""
        st.markdown("## 📊 Volume Analysis")
        st.markdown("Track your total workout volume over time (Weight × Reps)")
        
        volume_fig = self.progression_viz.create_volume_chart(self.filtered_df)
        st.plotly_chart(volume_fig, use_container_width=True)
        
        # Add volume insights
        if not self.filtered_df.empty:
            # Calculate volume per workout
            volume_data = self.filtered_df.groupby('date').apply(
                lambda x: (x['weight'] * x['reps']).sum()
            ).reset_index()
            volume_data.columns = ['date', 'volume']
            
            # Get insights
            avg_volume = int(volume_data['volume'].mean())
            max_volume = int(volume_data['volume'].max())
            max_volume_date = volume_data.loc[volume_data['volume'].idxmax(), 'date'].strftime('%Y-%m-%d')
            
            # Display insights
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{avg_volume:,}</div>
                    <div class="metric-label">Average Volume (kg)</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{max_volume:,}</div>
                    <div class="metric-label">Max Volume ({max_volume_date})</div>
                </div>
                """, unsafe_allow_html=True)

    def display_detailed_exercise_data(self):
        """Display detailed exercise data section"""
        st.markdown("## 📋 Detailed Exercise Data")
        st.markdown("Complete breakdown of all exercises and their statistics")
        
        if self.filtered_df.empty:
            st.warning("⚠️ No exercise data available for the selected filters.")
            return
            
        # Add search functionality
        search_term = st.text_input("Search for exercises:", "")
        
        exercise_details = self.analyzer.get_exercise_details(self.filtered_df)
        
        # Filter based on search term
        if search_term:
            exercise_details = exercise_details[exercise_details['Exercise'].str.contains(search_term, case=False)]
        
        # Display the data with improved styling
        st.dataframe(exercise_details, use_container_width=True)
        
        # Add export functionality
        if not exercise_details.empty:
            csv = exercise_details.to_csv(index=False)
            st.download_button(
                label="Download Exercise Data as CSV",
                data=csv,
                file_name="workout_exercise_data.csv",
                mime="text/csv",
            )

    def display_app_comparison(self):
        """Display app comparison section"""
        st.markdown("## 📱 App Comparison")
        st.markdown("Compare statistics across different workout tracking apps")
        
        app_stats = self.analyzer.get_app_comparison(self.filtered_df)
        
        # Create a more visual representation
        if not app_stats.empty:
            # Display as cards instead of a table
            cols = st.columns(len(app_stats))
            
            for i, (_, row) in enumerate(app_stats.iterrows()):
                with cols[i]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>{row['App']}</h3>
                        <div class="metric-value">{int(row['Total Sets']):,}</div>
                        <div class="metric-label">Total Sets</div>
                        <hr>
                        <div class="metric-value">{int(row['Total Volume']):,}</div>
                        <div class="metric-label">Total Volume</div>
                        <hr>
                        <div class="metric-value">{row['Workout Days']}</div>
                        <div class="metric-label">Workout Days</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ No app data available for the selected filters.")

    def run(self):
        """Run the dashboard application"""
        # Load custom CSS
        load_css()
        
        # Setup sidebar filters
        self.render_sidebar()

        # Display overview statistics at the top (always visible)
        self.display_overview_statistics()
        
        # Check if data is available after filtering
        if self.filtered_df.empty:
            st.warning("⚠️ No workout data available for the selected filters. Try adjusting your filter settings.")
            return
        
        # Create tabs for different visualization groups with icons
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📅 Calendar & Activity", 
            "📊 Workout Frequency", 
            "💪 Exercise Analysis",
            "📈 Volume Analysis",
            "📋 Detailed Data",
            "📱 App Comparison"
        ])
        
        # Tab 1: Calendar & Activity Blocks
        with tab1:
            # Calendar view
            self.display_calendar_view()
            
            # Weekly blocks
            self.display_weekly_blocks()
        
        # Tab 2: Workout Frequency
        with tab2:
            self.display_workout_frequency()
            self.display_exercise_distribution()
        
        # Tab 3: Exercise Analysis
        with tab3:
            self.display_exercise_analysis()
        
        # Tab 4: Volume Analysis
        with tab4:
            self.display_volume_analysis()
        
        # Tab 5: Detailed Data
        with tab5:
            self.display_detailed_exercise_data()
            
        # Tab 6: App Comparison
        with tab6:
            self.display_app_comparison()


# Run the dashboard
if __name__ == "__main__":
    dashboard = WorkoutDashboard()
    dashboard.run()
