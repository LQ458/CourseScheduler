import streamlit as st
import pandas as pd
import uuid

class DataManager:
    """
    Class to manage the data for the scheduling system
    """
    
    def __init__(self):
        # Initialize data storages if not in session state
        if 'teachers_data' not in st.session_state:
            st.session_state.teachers_data = []
        if 'rooms_data' not in st.session_state:
            st.session_state.rooms_data = []
        if 'classes_data' not in st.session_state:
            st.session_state.classes_data = []
        if 'courses_data' not in st.session_state:
            st.session_state.courses_data = []
    
    def add_teacher(self, name, subjects):
        """
        Add a teacher to the system
        
        Args:
            name (str): Teacher's name
            subjects (list): List of subjects the teacher can teach
        """
        teacher_id = str(uuid.uuid4())
        
        teacher = {
            'id': teacher_id,
            'name': name,
            'subjects': subjects
        }
        
        st.session_state.teachers_data.append(teacher)
        return teacher_id
    
    def remove_teacher(self, teacher_name):
        """
        Remove a teacher from the system
        
        Args:
            teacher_name (str): Name of the teacher to remove
        """
        st.session_state.teachers_data = [
            t for t in st.session_state.teachers_data if t['name'] != teacher_name
        ]
    
    def get_teachers(self):
        """
        Get all teachers in the system
        
        Returns:
            list: List of teacher dictionaries
        """
        return st.session_state.teachers_data
    
    def add_room(self, name, capacity):
        """
        Add a room to the system
        
        Args:
            name (str): Room name/number
            capacity (int): Room capacity
        """
        room_id = str(uuid.uuid4())
        
        room = {
            'id': room_id,
            'name': name,
            'capacity': capacity
        }
        
        st.session_state.rooms_data.append(room)
        return room_id
    
    def remove_room(self, room_name):
        """
        Remove a room from the system
        
        Args:
            room_name (str): Name of the room to remove
        """
        st.session_state.rooms_data = [
            r for r in st.session_state.rooms_data if r['name'] != room_name
        ]
    
    def get_rooms(self):
        """
        Get all rooms in the system
        
        Returns:
            list: List of room dictionaries
        """
        return st.session_state.rooms_data
    
    def add_class(self, name, size):
        """
        Add a class to the system
        
        Args:
            name (str): Class name
            size (int): Number of students in the class
        """
        class_id = str(uuid.uuid4())
        
        class_obj = {
            'id': class_id,
            'name': name,
            'size': size
        }
        
        st.session_state.classes_data.append(class_obj)
        return class_id
    
    def remove_class(self, class_name):
        """
        Remove a class from the system
        
        Args:
            class_name (str): Name of the class to remove
        """
        st.session_state.classes_data = [
            c for c in st.session_state.classes_data if c['name'] != class_name
        ]
        
        # Also remove all courses assigned to this class
        st.session_state.courses_data = [
            c for c in st.session_state.courses_data if c['class'] != class_name
        ]
    
    def get_classes(self):
        """
        Get all classes in the system
        
        Returns:
            list: List of class dictionaries
        """
        return st.session_state.classes_data
    
    def add_course(self, name, teacher, assigned_class, duration, frequency):
        """
        Add a course to the system
        
        Args:
            name (str): Course name
            teacher (str): Teacher's name
            assigned_class (str): Class name to assign the course to
            duration (int): Course duration in minutes
            frequency (int): Number of times per week
        """
        course_id = str(uuid.uuid4())
        
        course = {
            'id': course_id,
            'name': name,
            'teacher': teacher,
            'class': assigned_class,
            'duration': duration,
            'frequency': frequency
        }
        
        st.session_state.courses_data.append(course)
        return course_id
    
    def remove_course(self, course_name, class_name):
        """
        Remove a course from the system
        
        Args:
            course_name (str): Name of the course to remove
            class_name (str): Name of the class the course is assigned to
        """
        st.session_state.courses_data = [
            c for c in st.session_state.courses_data 
            if not (c['name'] == course_name and c['class'] == class_name)
        ]
    
    def get_courses(self):
        """
        Get all courses in the system
        
        Returns:
            list: List of course dictionaries
        """
        return st.session_state.courses_data
    
    def clear_all_data(self):
        """
        Clear all data from the system
        """
        st.session_state.teachers_data = []
        st.session_state.rooms_data = []
        st.session_state.classes_data = []
        st.session_state.courses_data = []
