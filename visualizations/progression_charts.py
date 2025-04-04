import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


class ProgressionVisualizer:
    """Class for creating progression and frequency visualizations"""

    def create_monthly_frequency_chart(self, df):
        """Create monthly workout frequency chart"""
        df['month_year'] = df['date'].dt.to_period('M')
        monthly_workouts = df.groupby('month_year')['date'].nunique().reset_index()
        monthly_workouts['month_year'] = monthly_workouts['month_year'].astype(str)

        fig = px.line(monthly_workouts, x='month_year', y='date', title='Monthly Workout Frequency',
                      labels={'date': 'Number of Workouts', 'month_year': 'Month'})
        fig.update_xaxes(tickangle=45)
        return fig

    def create_weekly_frequency_chart(self, df):
        """Create weekly workout frequency chart"""
        df['week_start'] = df['date'].dt.to_period('W').astype(str).str.split('/').str[0]
        weekly_workouts = df.groupby('week_start')['date'].nunique().reset_index()

        fig = px.bar(weekly_workouts, x='week_start', y='date', title='Weekly Workout Frequency',
                     labels={'date': 'Number of Workouts', 'week_start': 'Week Starting'})
        fig.update_xaxes(tickangle=45)
        return fig

    def create_exercise_distribution_chart(self, df):
        """Create exercise distribution chart"""
        exercise_counts = df['exercise'].value_counts().head(10)
        chart_df = pd.DataFrame({
            'Exercise': exercise_counts.index,
            'Count': exercise_counts.values
        })
        fig = px.bar(chart_df, x='Exercise', y='Count', title='Top 10 Most Performed Exercises',
                     labels={'Exercise': 'Exercise', 'Count': 'Number of Sets'})
        return fig

    def create_exercise_progression_chart(self, df, selected_exercise):
        """Create exercise progression chart"""
        exercise_progression = df[df['exercise'] == selected_exercise].groupby('date').agg(
            {'weight': 'max', 'one_rm': 'max'}).reset_index()

        # Create figure with secondary y-axis
        fig = go.Figure()

        # Add traces
        fig.add_trace(
            go.Scatter(x=exercise_progression['date'], y=exercise_progression['weight'], name="Working Weight",
                       line=dict(color='blue')))

        fig.add_trace(go.Scatter(x=exercise_progression['date'], y=exercise_progression['one_rm'], name="Estimated 1RM",
                                 line=dict(color='red')))

        # Update layout
        fig.update_layout(title=f'Weight and 1RM Progression', xaxis_title="Date", yaxis_title="Weight (kg)",
                          yaxis2=dict(title="1RM (kg)", overlaying="y", side="right"))

        return fig

    def create_volume_chart(self, df):
        """Create volume analysis chart"""
        volume_data = df.groupby('date').agg(
            {'weight': lambda x: (x * df.loc[x.index, 'reps']).sum(), 'exercise': 'count'}).reset_index()

        fig = px.scatter(volume_data, x='date', y='weight', size='exercise', title='Daily Volume (Weight × Reps)',
                         labels={'weight': 'Total Volume (kg)', 'exercise': 'Number of Exercises'})
        return fig
