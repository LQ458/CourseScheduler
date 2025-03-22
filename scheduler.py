import pandas as pd
import numpy as np
import datetime
import random

class ScheduleGenerator:
    """
    Class to generate conflict-free schedules
    """
    
    def __init__(self, teachers, rooms, classes, courses, 
                 start_time, end_time, period_length, break_length,
                 lunch_period="No lunch", lunch_duration=30):
        """
        Initialize the scheduler with the necessary data
        
        Args:
            teachers (list): List of teacher dictionaries
            rooms (list): List of room dictionaries
            classes (list): List of class dictionaries
            courses (list): List of course dictionaries
            start_time (time): School day start time
            end_time (time): School day end time
            period_length (int): Length of each period in minutes
            break_length (int): Length of breaks between periods in minutes
            lunch_period (str): When to schedule lunch
            lunch_duration (int): Length of lunch in minutes
        """
        self.teachers = teachers
        self.rooms = rooms
        self.classes = classes
        self.courses = courses
        self.start_time = start_time
        self.end_time = end_time
        self.period_length = period_length
        self.break_length = break_length
        self.lunch_period = lunch_period
        self.lunch_duration = lunch_duration
        
        # Days of the week
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        # Generate time slots
        self.time_slots = self._generate_time_slots()
        
        # Initialize schedule data structures
        self.class_schedule = {cls['name']: {day: {time: None for time in self.time_slots} 
                                            for day in self.days} 
                              for cls in self.classes}
        
        self.teacher_schedule = {teacher['name']: {day: {time: None for time in self.time_slots} 
                                                for day in self.days} 
                                for teacher in self.teachers}
        
        self.room_schedule = {room['name']: {day: {time: None for time in self.time_slots} 
                                           for day in self.days} 
                             for room in self.rooms}
        
    def _generate_time_slots(self):
        """
        Generate time slots based on start time, end time, period length, and breaks
        
        Returns:
            list: List of time slots in format "HH:MM-HH:MM"
        """
        time_slots = []
        
        # Convert start_time and end_time to minutes since midnight
        start_minutes = self.start_time.hour * 60 + self.start_time.minute
        end_minutes = self.end_time.hour * 60 + self.end_time.minute
        
        current_minutes = start_minutes
        period_counter = 1
        
        while current_minutes + self.period_length <= end_minutes:
            # Calculate end of period
            period_end = current_minutes + self.period_length
            
            # Format times
            start_time = f"{current_minutes // 60:02d}:{current_minutes % 60:02d}"
            end_time = f"{period_end // 60:02d}:{period_end % 60:02d}"
            
            # Add time slot
            time_slots.append(f"{start_time}-{end_time}")
            
            # If this is the lunch period, add lunch break
            if (self.lunch_period == "After period 3" and period_counter == 3) or \
               (self.lunch_period == "After period 4" and period_counter == 4):
                current_minutes = period_end + self.lunch_duration
            else:
                current_minutes = period_end + self.break_length
            
            period_counter += 1
        
        return time_slots
    
    def _is_slot_available(self, class_name, teacher_name, room_name, day, time_slot):
        """
        Check if a time slot is available for scheduling
        
        Args:
            class_name (str): Name of the class
            teacher_name (str): Name of the teacher
            room_name (str): Name of the room
            day (str): Day of the week
            time_slot (str): Time slot
            
        Returns:
            bool: True if slot is available, False otherwise
        """
        # Check if class is already scheduled at this time
        if self.class_schedule[class_name][day][time_slot] is not None:
            return False
        
        # Check if teacher is already scheduled at this time
        if self.teacher_schedule[teacher_name][day][time_slot] is not None:
            return False
        
        # Check if room is already scheduled at this time
        if self.room_schedule[room_name][day][time_slot] is not None:
            return False
        
        return True
    
    def _assign_time_slot(self, course, class_name, teacher_name, room_name, day, time_slot):
        """
        Assign a course to a specific time slot
        
        Args:
            course (dict): Course to assign
            class_name (str): Name of the class
            teacher_name (str): Name of the teacher
            room_name (str): Name of the room
            day (str): Day of the week
            time_slot (str): Time slot
        """
        # Record the assignment in all schedules
        assignment = {
            'course': course['name'],
            'teacher': teacher_name,
            'room': room_name,
            'class': class_name,
            'day': day,
            'time': time_slot
        }
        
        self.class_schedule[class_name][day][time_slot] = assignment
        self.teacher_schedule[teacher_name][day][time_slot] = assignment
        self.room_schedule[room_name][day][time_slot] = assignment
    
    def _find_available_room(self, class_size, day, time_slot):
        """
        Find an available room for a class
        
        Args:
            class_size (int): Size of the class
            day (str): Day of the week
            time_slot (str): Time slot
            
        Returns:
            str: Name of an available room, or None if no room is available
        """
        # Find rooms with sufficient capacity
        suitable_rooms = [room for room in self.rooms if room['capacity'] >= class_size]
        
        # Shuffle rooms for randomness
        random.shuffle(suitable_rooms)
        
        for room in suitable_rooms:
            if self.room_schedule[room['name']][day][time_slot] is None:
                return room['name']
        
        return None
    
    def _get_class_size(self, class_name):
        """
        Get the size of a class
        
        Args:
            class_name (str): Name of the class
            
        Returns:
            int: Size of the class
        """
        for cls in self.classes:
            if cls['name'] == class_name:
                return cls['size']
        return 0
    
    def generate_schedule(self):
        """
        Generate a conflict-free schedule
        
        Returns:
            tuple: (schedule, conflicts) where schedule is a list of assignments and conflicts is a list of conflicts
        """
        # Sort courses by frequency and then by name (for deterministic output)
        sorted_courses = sorted(self.courses, key=lambda x: (-x['frequency'], x['name']))
        
        # Initialize empty schedule and conflicts list
        schedule = []
        conflicts = []
        
        # Track assigned sessions for each course
        course_sessions = {(course['name'], course['class']): 0 for course in self.courses}
        
        # First pass: Try to schedule each course
        for course in sorted_courses:
            class_name = course['class']
            teacher_name = course['teacher']
            required_sessions = course['frequency']
            class_size = self._get_class_size(class_name)
            
            # Keep track of already assigned days to avoid scheduling the same course twice in a day
            assigned_days = set()
            
            # Try to schedule each session
            for _ in range(required_sessions):
                # Randomize days and time slots for more variety
                days = self.days.copy()
                random.shuffle(days)
                
                session_scheduled = False
                
                for day in days:
                    # Skip days where this course is already scheduled
                    if day in assigned_days and len(assigned_days) < len(self.days):
                        continue
                    
                    time_slots = self.time_slots.copy()
                    random.shuffle(time_slots)
                    
                    for time_slot in time_slots:
                        # Find an available room
                        room_name = self._find_available_room(class_size, day, time_slot)
                        
                        if room_name and self._is_slot_available(class_name, teacher_name, room_name, day, time_slot):
                            # Assign the course
                            self._assign_time_slot(course, class_name, teacher_name, room_name, day, time_slot)
                            course_sessions[(course['name'], course['class'])] += 1
                            assigned_days.add(day)
                            session_scheduled = True
                            break
                    
                    if session_scheduled:
                        break
                
                if not session_scheduled:
                    # Could not schedule this session, record a conflict
                    conflicts.append({
                        'type': 'Unscheduled Session',
                        'day': 'N/A',
                        'time': 'N/A',
                        'description': f"Could not schedule a session for {course['name']} (Class: {class_name}, Teacher: {teacher_name})"
                    })
        
        # Check for scheduling conflicts and collect the schedule
        for class_name in self.class_schedule:
            for day in self.days:
                for time_slot in self.time_slots:
                    assignment = self.class_schedule[class_name][day][time_slot]
                    
                    if assignment:
                        schedule.append(assignment)
        
        # Check for teacher conflicts
        for teacher_name in self.teacher_schedule:
            for day in self.days:
                for time_slot in self.time_slots:
                    classes_at_time = []
                    
                    for class_name in self.class_schedule:
                        if self.class_schedule[class_name][day][time_slot] and \
                           self.class_schedule[class_name][day][time_slot]['teacher'] == teacher_name:
                            classes_at_time.append(class_name)
                    
                    if len(classes_at_time) > 1:
                        conflicts.append({
                            'type': 'Teacher Conflict',
                            'day': day,
                            'time': time_slot,
                            'description': f"Teacher {teacher_name} is scheduled for multiple classes: {', '.join(classes_at_time)}"
                        })
        
        # Check for room conflicts
        for room_name in self.room_schedule:
            for day in self.days:
                for time_slot in self.time_slots:
                    classes_at_time = []
                    
                    for class_name in self.class_schedule:
                        if self.class_schedule[class_name][day][time_slot] and \
                           self.class_schedule[class_name][day][time_slot]['room'] == room_name:
                            classes_at_time.append(class_name)
                    
                    if len(classes_at_time) > 1:
                        conflicts.append({
                            'type': 'Room Conflict',
                            'day': day,
                            'time': time_slot,
                            'description': f"Room {room_name} is scheduled for multiple classes: {', '.join(classes_at_time)}"
                        })
        
        # Check for course frequency fulfillment
        for course_key, assigned_sessions in course_sessions.items():
            course_name, class_name = course_key
            required_sessions = next((c['frequency'] for c in self.courses if c['name'] == course_name and c['class'] == class_name), 0)
            
            if assigned_sessions < required_sessions:
                conflicts.append({
                    'type': 'Frequency Not Met',
                    'day': 'N/A',
                    'time': 'N/A',
                    'description': f"Course {course_name} (Class: {class_name}) was scheduled for {assigned_sessions}/{required_sessions} required sessions"
                })
        
        return schedule, conflicts
