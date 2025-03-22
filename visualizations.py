import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

class ScheduleVisualizer:
    """
    Class to create visualizations of class schedules
    """
    
    def __init__(self, schedule):
        """
        Initialize the visualizer with schedule data
        
        Args:
            schedule (list): List of schedule assignments
        """
        self.schedule = schedule
        self.df = self._create_dataframe()
        
        # Define a color palette for consistent colors
        self.course_colors = {}
        self._assign_colors()
    
    def _create_dataframe(self):
        """
        Convert schedule list to pandas DataFrame
        
        Returns:
            DataFrame: Schedule data in DataFrame format
        """
        if not self.schedule:
            return pd.DataFrame()
        
        return pd.DataFrame(self.schedule)
    
    def _assign_colors(self):
        """
        Assign consistent colors to courses
        """
        if self.df.empty:
            return
        
        # Get unique courses
        unique_courses = self.df['course'].unique()
        
        # Create a colorscale with enough colors
        colorscale = px.colors.qualitative.Plotly
        if len(unique_courses) > len(colorscale):
            # If we need more colors, add from another palette
            colorscale = colorscale + px.colors.qualitative.Set3
        
        # Assign a color to each course
        for i, course in enumerate(unique_courses):
            self.course_colors[course] = colorscale[i % len(colorscale)]
    
    def _parse_time_slot(self, time_slot):
        """
        Parse time slot string to start and end times
        
        Args:
            time_slot (str): Time slot in format "HH:MM-HH:MM"
            
        Returns:
            tuple: (start_datetime, end_datetime)
        """
        start_time_str, end_time_str = time_slot.split('-')
        
        base_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        
        start_hour, start_minute = map(int, start_time_str.split(':'))
        end_hour, end_minute = map(int, end_time_str.split(':'))
        
        start_datetime = base_date + timedelta(hours=start_hour, minutes=start_minute)
        end_datetime = base_date + timedelta(hours=end_hour, minutes=end_minute)
        
        return start_datetime, end_datetime
    
    def get_class_schedule_data(self, class_name):
        """
        Get schedule data for a specific class
        
        Args:
            class_name (str): Name of the class
            
        Returns:
            DataFrame: Filtered schedule data
        """
        if self.df.empty:
            return pd.DataFrame()
        
        class_df = self.df[self.df['class'] == class_name].copy()
        
        if class_df.empty:
            return pd.DataFrame()
        
        # Create a pivot table for better readability
        pivot_df = class_df.pivot_table(
            index='time',
            columns='day',
            values='course',
            aggfunc='first'
        ).reset_index()
        
        # Sort by time slot
        def extract_start_time(time_slot):
            start_time, _ = time_slot.split('-')
            return datetime.strptime(start_time, "%H:%M")
        
        pivot_df['sort_key'] = pivot_df['time'].apply(extract_start_time)
        pivot_df = pivot_df.sort_values('sort_key').drop('sort_key', axis=1)
        
        return pivot_df
    
    def get_teacher_schedule_data(self, teacher_name):
        """
        Get schedule data for a specific teacher
        
        Args:
            teacher_name (str): Name of the teacher
            
        Returns:
            DataFrame: Filtered schedule data
        """
        if self.df.empty:
            return pd.DataFrame()
        
        teacher_df = self.df[self.df['teacher'] == teacher_name].copy()
        
        if teacher_df.empty:
            return pd.DataFrame()
        
        # Create a pivot table for better readability
        pivot_df = teacher_df.pivot_table(
            index='time',
            columns='day',
            values=['course', 'class'],
            aggfunc='first'
        ).reset_index()
        
        # Sort by time slot
        def extract_start_time(time_slot):
            start_time, _ = time_slot.split('-')
            return datetime.strptime(start_time, "%H:%M")
        
        pivot_df['sort_key'] = pivot_df['time'].apply(extract_start_time)
        pivot_df = pivot_df.sort_values('sort_key').drop('sort_key', axis=1)
        
        return pivot_df
    
    def get_room_schedule_data(self, room_name):
        """
        Get schedule data for a specific room
        
        Args:
            room_name (str): Name of the room
            
        Returns:
            DataFrame: Filtered schedule data
        """
        if self.df.empty:
            return pd.DataFrame()
        
        room_df = self.df[self.df['room'] == room_name].copy()
        
        if room_df.empty:
            return pd.DataFrame()
        
        # Create a pivot table for better readability
        pivot_df = room_df.pivot_table(
            index='time',
            columns='day',
            values=['course', 'class'],
            aggfunc='first'
        ).reset_index()
        
        # Sort by time slot
        def extract_start_time(time_slot):
            start_time, _ = time_slot.split('-')
            return datetime.strptime(start_time, "%H:%M")
        
        pivot_df['sort_key'] = pivot_df['time'].apply(extract_start_time)
        pivot_df = pivot_df.sort_values('sort_key').drop('sort_key', axis=1)
        
        return pivot_df
    
    def get_full_schedule_data(self):
        """
        Get the full schedule data
        
        Returns:
            DataFrame: Full schedule data
        """
        return self.df
    
    def generate_class_schedule(self, class_name):
        """
        Generate a visual schedule for a class
        
        Args:
            class_name (str): Name of the class
            
        Returns:
            Figure: Plotly figure object
        """
        if self.df.empty:
            fig = go.Figure()
            fig.update_layout(
                title=f"No schedule data available for {class_name}",
                xaxis_title="Day",
                yaxis_title="Time",
                height=600
            )
            return fig
        
        # Filter data for the selected class
        class_df = self.df[self.df['class'] == class_name].copy()
        
        if class_df.empty:
            fig = go.Figure()
            fig.update_layout(
                title=f"No schedule data available for {class_name}",
                xaxis_title="Day",
                yaxis_title="Time",
                height=600
            )
            return fig
        
        # Create a figure with one trace per course
        fig = go.Figure()
        
        # Get unique days for ordering
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        day_order = {day: i for i, day in enumerate(days)}
        
        # Process each row in the filtered dataframe
        for _, row in class_df.iterrows():
            course = row['course']
            teacher = row['teacher']
            room = row['room']
            day = row['day']
            time_slot = row['time']
            
            # Parse time slot
            start_time, end_time = self._parse_time_slot(time_slot)
            
            # Create hover text
            hover_text = f"Course: {course}<br>Teacher: {teacher}<br>Room: {room}<br>Time: {time_slot}"
            
            # Add a rectangle for this course
            fig.add_trace(go.Scatter(
                x=[day_order[day], day_order[day], day_order[day] + 0.8, day_order[day] + 0.8, day_order[day]],
                y=[start_time.hour + start_time.minute/60, end_time.hour + end_time.minute/60, 
                   end_time.hour + end_time.minute/60, start_time.hour + start_time.minute/60, 
                   start_time.hour + start_time.minute/60],
                fill="toself",
                fillcolor=self.course_colors.get(course, "lightgrey"),
                line=dict(color="white", width=2),
                mode="lines",
                name=course,
                text=hover_text,
                hoverinfo="text"
            ))
            
            # Add text label
            fig.add_trace(go.Scatter(
                x=[day_order[day] + 0.4],
                y=[(start_time.hour + start_time.minute/60 + end_time.hour + end_time.minute/60) / 2],
                text=course,
                mode="text",
                showlegend=False,
                hoverinfo="none"
            ))
        
        # Update layout
        fig.update_layout(
            title=f"Schedule for {class_name}",
            xaxis=dict(
                title="Day",
                tickvals=list(day_order.values()),
                ticktext=list(day_order.keys()),
                range=[-0.2, 5]
            ),
            yaxis=dict(
                title="Time",
                range=[7, 17],  # 7 AM to 5 PM
                dtick=1,
                tickvals=list(range(8, 17)),
                ticktext=[f"{hour}:00" for hour in range(8, 17)]
            ),
            height=600,
            legend=dict(
                title="Courses",
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            )
        )
        
        return fig
    
    def generate_teacher_schedule(self, teacher_name):
        """
        Generate a visual schedule for a teacher
        
        Args:
            teacher_name (str): Name of the teacher
            
        Returns:
            Figure: Plotly figure object
        """
        if self.df.empty:
            fig = go.Figure()
            fig.update_layout(
                title=f"No schedule data available for {teacher_name}",
                xaxis_title="Day",
                yaxis_title="Time",
                height=600
            )
            return fig
        
        # Filter data for the selected teacher
        teacher_df = self.df[self.df['teacher'] == teacher_name].copy()
        
        if teacher_df.empty:
            fig = go.Figure()
            fig.update_layout(
                title=f"No schedule data available for {teacher_name}",
                xaxis_title="Day",
                yaxis_title="Time",
                height=600
            )
            return fig
        
        # Create a figure with one trace per course-class combination
        fig = go.Figure()
        
        # Get unique days for ordering
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        day_order = {day: i for i, day in enumerate(days)}
        
        # Process each row in the filtered dataframe
        for _, row in teacher_df.iterrows():
            course = row['course']
            class_name = row['class']
            room = row['room']
            day = row['day']
            time_slot = row['time']
            
            # Parse time slot
            start_time, end_time = self._parse_time_slot(time_slot)
            
            # Create hover text
            hover_text = f"Course: {course}<br>Class: {class_name}<br>Room: {room}<br>Time: {time_slot}"
            
            # Add a rectangle for this course
            fig.add_trace(go.Scatter(
                x=[day_order[day], day_order[day], day_order[day] + 0.8, day_order[day] + 0.8, day_order[day]],
                y=[start_time.hour + start_time.minute/60, end_time.hour + end_time.minute/60, 
                   end_time.hour + end_time.minute/60, start_time.hour + start_time.minute/60, 
                   start_time.hour + start_time.minute/60],
                fill="toself",
                fillcolor=self.course_colors.get(course, "lightgrey"),
                line=dict(color="white", width=2),
                mode="lines",
                name=f"{course} ({class_name})",
                text=hover_text,
                hoverinfo="text"
            ))
            
            # Add text label
            fig.add_trace(go.Scatter(
                x=[day_order[day] + 0.4],
                y=[(start_time.hour + start_time.minute/60 + end_time.hour + end_time.minute/60) / 2],
                text=f"{course}<br>{class_name}",
                mode="text",
                showlegend=False,
                hoverinfo="none"
            ))
        
        # Update layout
        fig.update_layout(
            title=f"Schedule for Teacher: {teacher_name}",
            xaxis=dict(
                title="Day",
                tickvals=list(day_order.values()),
                ticktext=list(day_order.keys()),
                range=[-0.2, 5]
            ),
            yaxis=dict(
                title="Time",
                range=[7, 17],  # 7 AM to 5 PM
                dtick=1,
                tickvals=list(range(8, 17)),
                ticktext=[f"{hour}:00" for hour in range(8, 17)]
            ),
            height=600,
            legend=dict(
                title="Courses",
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            )
        )
        
        return fig
    
    def generate_room_schedule(self, room_name):
        """
        Generate a visual schedule for a room
        
        Args:
            room_name (str): Name of the room
            
        Returns:
            Figure: Plotly figure object
        """
        if self.df.empty:
            fig = go.Figure()
            fig.update_layout(
                title=f"No schedule data available for {room_name}",
                xaxis_title="Day",
                yaxis_title="Time",
                height=600
            )
            return fig
        
        # Filter data for the selected room
        room_df = self.df[self.df['room'] == room_name].copy()
        
        if room_df.empty:
            fig = go.Figure()
            fig.update_layout(
                title=f"No schedule data available for {room_name}",
                xaxis_title="Day",
                yaxis_title="Time",
                height=600
            )
            return fig
        
        # Create a figure with one trace per course-class combination
        fig = go.Figure()
        
        # Get unique days for ordering
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        day_order = {day: i for i, day in enumerate(days)}
        
        # Process each row in the filtered dataframe
        for _, row in room_df.iterrows():
            course = row['course']
            class_name = row['class']
            teacher = row['teacher']
            day = row['day']
            time_slot = row['time']
            
            # Parse time slot
            start_time, end_time = self._parse_time_slot(time_slot)
            
            # Create hover text
            hover_text = f"Course: {course}<br>Class: {class_name}<br>Teacher: {teacher}<br>Time: {time_slot}"
            
            # Add a rectangle for this course
            fig.add_trace(go.Scatter(
                x=[day_order[day], day_order[day], day_order[day] + 0.8, day_order[day] + 0.8, day_order[day]],
                y=[start_time.hour + start_time.minute/60, end_time.hour + end_time.minute/60, 
                   end_time.hour + end_time.minute/60, start_time.hour + start_time.minute/60, 
                   start_time.hour + start_time.minute/60],
                fill="toself",
                fillcolor=self.course_colors.get(course, "lightgrey"),
                line=dict(color="white", width=2),
                mode="lines",
                name=f"{course} ({class_name})",
                text=hover_text,
                hoverinfo="text"
            ))
            
            # Add text label
            fig.add_trace(go.Scatter(
                x=[day_order[day] + 0.4],
                y=[(start_time.hour + start_time.minute/60 + end_time.hour + end_time.minute/60) / 2],
                text=f"{course}<br>{class_name}",
                mode="text",
                showlegend=False,
                hoverinfo="none"
            ))
        
        # Update layout
        fig.update_layout(
            title=f"Schedule for Room: {room_name}",
            xaxis=dict(
                title="Day",
                tickvals=list(day_order.values()),
                ticktext=list(day_order.keys()),
                range=[-0.2, 5]
            ),
            yaxis=dict(
                title="Time",
                range=[7, 17],  # 7 AM to 5 PM
                dtick=1,
                tickvals=list(range(8, 17)),
                ticktext=[f"{hour}:00" for hour in range(8, 17)]
            ),
            height=600,
            legend=dict(
                title="Courses",
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            )
        )
        
        return fig
