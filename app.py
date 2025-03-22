import streamlit as st
import pandas as pd
import numpy as np
from scheduler import ScheduleGenerator
from data_manager import DataManager
from visualizations import ScheduleVisualizer
import plotly.express as px
import plotly.graph_objects as go

# Set page title and layout
st.set_page_config(
    page_title="Class Scheduling System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'courses' not in st.session_state:
    st.session_state.courses = []
if 'teachers' not in st.session_state:
    st.session_state.teachers = []
if 'rooms' not in st.session_state:
    st.session_state.rooms = []
if 'classes' not in st.session_state:
    st.session_state.classes = []
if 'schedule' not in st.session_state:
    st.session_state.schedule = None
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "Class"  # Default view mode
if 'conflicts' not in st.session_state:
    st.session_state.conflicts = []

# Initialize the data manager
data_manager = DataManager()

# Title and introduction
st.title("Class Scheduling System")
st.markdown("""
This system helps generate conflict-free timetables for multiple classes, accounting for:
- Teacher availability
- Room availability
- Class time constraints
- Course frequencies (3x or 5x per week)
""")

# Sidebar for navigation
st.sidebar.title("Navigation")
section = st.sidebar.radio(
    "Select a section:",
    ["Input Data", "Generate Schedule", "View Schedule", "Manage Conflicts"]
)

# Define time slots
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
TIME_SLOTS = [
    "8:00-8:50", "9:00-9:50", "10:00-10:50", "11:00-11:50",
    "12:00-12:50", "1:00-1:50", "2:00-2:50", "3:00-3:50"
]

# Input Data Section
if section == "Input Data":
    st.header("Input Data")
    
    # Create tabs for different data inputs
    input_tab = st.tabs(["Teachers", "Rooms", "Classes", "Courses"])
    
    # Teachers tab
    with input_tab[0]:
        st.subheader("Manage Teachers")
        
        # Input for adding new teacher
        with st.form("add_teacher_form"):
            new_teacher_name = st.text_input("Teacher Name")
            new_teacher_subjects = st.text_input("Subjects (comma-separated)")
            teacher_submit = st.form_submit_button("Add Teacher")
            
            if teacher_submit and new_teacher_name:
                subjects = [s.strip() for s in new_teacher_subjects.split(",") if s.strip()]
                data_manager.add_teacher(new_teacher_name, subjects)
                st.success(f"Teacher {new_teacher_name} added!")
                st.session_state.teachers = data_manager.get_teachers()
                st.rerun()
        
        # Display existing teachers
        if st.session_state.teachers:
            teacher_df = pd.DataFrame(st.session_state.teachers)
            st.dataframe(teacher_df)
            
            # Option to remove teachers
            teacher_to_remove = st.selectbox(
                "Select teacher to remove",
                options=[t['name'] for t in st.session_state.teachers],
                index=None
            )
            if st.button("Remove Teacher") and teacher_to_remove:
                data_manager.remove_teacher(teacher_to_remove)
                st.success(f"Teacher {teacher_to_remove} removed!")
                st.session_state.teachers = data_manager.get_teachers()
                st.rerun()
        else:
            st.info("No teachers added yet. Add your first teacher above.")
    
    # Rooms tab
    with input_tab[1]:
        st.subheader("Manage Rooms")
        
        # Input for adding new room
        with st.form("add_room_form"):
            new_room_name = st.text_input("Room Name/Number")
            new_room_capacity = st.number_input("Capacity", min_value=1, value=30)
            room_submit = st.form_submit_button("Add Room")
            
            if room_submit and new_room_name:
                data_manager.add_room(new_room_name, new_room_capacity)
                st.success(f"Room {new_room_name} added!")
                st.session_state.rooms = data_manager.get_rooms()
                st.rerun()
        
        # Display existing rooms
        if st.session_state.rooms:
            room_df = pd.DataFrame(st.session_state.rooms)
            st.dataframe(room_df)
            
            # Option to remove rooms
            room_to_remove = st.selectbox(
                "Select room to remove",
                options=[r['name'] for r in st.session_state.rooms],
                index=None
            )
            if st.button("Remove Room") and room_to_remove:
                data_manager.remove_room(room_to_remove)
                st.success(f"Room {room_to_remove} removed!")
                st.session_state.rooms = data_manager.get_rooms()
                st.rerun()
        else:
            st.info("No rooms added yet. Add your first room above.")
    
    # Classes tab
    with input_tab[2]:
        st.subheader("Manage Classes")
        
        # Input for adding new class
        with st.form("add_class_form"):
            new_class_name = st.text_input("Class Name")
            new_class_size = st.number_input("Number of Students", min_value=1, value=25)
            class_submit = st.form_submit_button("Add Class")
            
            if class_submit and new_class_name:
                data_manager.add_class(new_class_name, new_class_size)
                st.success(f"Class {new_class_name} added!")
                st.session_state.classes = data_manager.get_classes()
                st.rerun()
        
        # Display existing classes
        if st.session_state.classes:
            class_df = pd.DataFrame(st.session_state.classes)
            st.dataframe(class_df)
            
            # Option to remove classes
            class_to_remove = st.selectbox(
                "Select class to remove",
                options=[c['name'] for c in st.session_state.classes],
                index=None
            )
            if st.button("Remove Class") and class_to_remove:
                data_manager.remove_class(class_to_remove)
                st.success(f"Class {class_to_remove} removed!")
                st.session_state.classes = data_manager.get_classes()
                st.rerun()
        else:
            st.info("No classes added yet. Add your first class above.")
    
    # Courses tab
    with input_tab[3]:
        st.subheader("Manage Courses")
        
        # Input for adding new course
        with st.form("add_course_form"):
            new_course_name = st.text_input("Course Name")
            new_course_teacher = st.selectbox(
                "Select Teacher",
                options=[t['name'] for t in st.session_state.teachers] if st.session_state.teachers else ["No teachers available"],
                index=0 if st.session_state.teachers else None,
                disabled=not st.session_state.teachers
            )
            assigned_class = st.selectbox(
                "Assign to Class",
                options=[c['name'] for c in st.session_state.classes] if st.session_state.classes else ["No classes available"],
                index=0 if st.session_state.classes else None,
                disabled=not st.session_state.classes
            )
            course_duration = st.selectbox("Duration (minutes)", options=[50, 60, 90], index=0)
            course_frequency = st.selectbox("Frequency (per week)", options=[1, 2, 3, 4, 5], index=2)
            course_submit = st.form_submit_button("Add Course")
            
            if course_submit and new_course_name and new_course_teacher != "No teachers available" and assigned_class != "No classes available":
                data_manager.add_course(
                    name=new_course_name,
                    teacher=new_course_teacher,
                    assigned_class=assigned_class,
                    duration=course_duration,
                    frequency=course_frequency
                )
                st.success(f"Course {new_course_name} added!")
                st.session_state.courses = data_manager.get_courses()
                st.rerun()
        
        # Display existing courses
        if st.session_state.courses:
            course_df = pd.DataFrame(st.session_state.courses)
            st.dataframe(course_df)
            
            # Option to remove courses
            course_to_remove = st.selectbox(
                "Select course to remove",
                options=[f"{c['name']} ({c['class']})" for c in st.session_state.courses],
                index=None
            )
            if st.button("Remove Course") and course_to_remove:
                course_name = course_to_remove.split(" (")[0]
                class_name = course_to_remove.split("(")[1].replace(")", "")
                data_manager.remove_course(course_name, class_name)
                st.success(f"Course {course_to_remove} removed!")
                st.session_state.courses = data_manager.get_courses()
                st.rerun()
        else:
            st.info("No courses added yet. Add your first course above.")

    # Option to add sample data for demo
    st.subheader("Sample Data")
    if st.button("Load Sample Data"):
        # Add sample teachers
        sample_teachers = [
            {"name": "Dr. Smith", "subjects": ["Physics"]},
            {"name": "Mrs. Johnson", "subjects": ["Chemistry"]},
            {"name": "Mr. Davis", "subjects": ["Mathematics"]},
            {"name": "Ms. Wilson", "subjects": ["English"]},
            {"name": "Mr. Martinez", "subjects": ["PE"]},
            {"name": "Dr. Brown", "subjects": ["Biology"]},
            {"name": "Ms. Lee", "subjects": ["Chinese"]},
            {"name": "Mr. Harris", "subjects": ["History"]},
            {"name": "Mrs. Clark", "subjects": ["Electives"]}
        ]
        
        # Add sample rooms
        sample_rooms = [
            {"name": "Room 101", "capacity": 30},
            {"name": "Room 102", "capacity": 30},
            {"name": "Room 103", "capacity": 30},
            {"name": "Science Lab", "capacity": 25},
            {"name": "Gym", "capacity": 50},
            {"name": "Library", "capacity": 40},
            {"name": "Room 201", "capacity": 30},
            {"name": "Room 202", "capacity": 30}
        ]
        
        # Add sample classes
        sample_classes = [
            {"name": "Class 9A", "size": 25},
            {"name": "Class 9B", "size": 27},
            {"name": "Class 10A", "size": 23},
            {"name": "Class 10B", "size": 26}
        ]
        
        # Add sample courses
        sample_courses = [
            {"name": "Physics", "teacher": "Dr. Smith", "class": "Class 9A", "duration": 50, "frequency": 3},
            {"name": "Chemistry", "teacher": "Mrs. Johnson", "class": "Class 9A", "duration": 50, "frequency": 3},
            {"name": "Algebra", "teacher": "Mr. Davis", "class": "Class 9A", "duration": 50, "frequency": 5},
            {"name": "English", "teacher": "Ms. Wilson", "class": "Class 9A", "duration": 50, "frequency": 5},
            {"name": "PE", "teacher": "Mr. Martinez", "class": "Class 9A", "duration": 50, "frequency": 3},
            {"name": "Biology", "teacher": "Dr. Brown", "class": "Class 9A", "duration": 50, "frequency": 3},
            {"name": "Chinese", "teacher": "Ms. Lee", "class": "Class 9A", "duration": 50, "frequency": 5},
            {"name": "World History", "teacher": "Mr. Harris", "class": "Class 9A", "duration": 50, "frequency": 3},
            {"name": "Electives", "teacher": "Mrs. Clark", "class": "Class 9A", "duration": 50, "frequency": 3},
            
            {"name": "Physics", "teacher": "Dr. Smith", "class": "Class 9B", "duration": 50, "frequency": 3},
            {"name": "Chemistry", "teacher": "Mrs. Johnson", "class": "Class 9B", "duration": 50, "frequency": 3},
            {"name": "Algebra", "teacher": "Mr. Davis", "class": "Class 9B", "duration": 50, "frequency": 5},
            {"name": "English", "teacher": "Ms. Wilson", "class": "Class 9B", "duration": 50, "frequency": 5},
            {"name": "PE", "teacher": "Mr. Martinez", "class": "Class 9B", "duration": 50, "frequency": 3},
            {"name": "Biology", "teacher": "Dr. Brown", "class": "Class 9B", "duration": 50, "frequency": 3},
            {"name": "Chinese", "teacher": "Ms. Lee", "class": "Class 9B", "duration": 50, "frequency": 5},
            {"name": "World History", "teacher": "Mr. Harris", "class": "Class 9B", "duration": 50, "frequency": 3},
            {"name": "Electives", "teacher": "Mrs. Clark", "class": "Class 9B", "duration": 50, "frequency": 3}
        ]
        
        # Clear existing data
        data_manager.clear_all_data()
        
        # Add sample data
        for teacher in sample_teachers:
            data_manager.add_teacher(teacher["name"], teacher["subjects"])
        
        for room in sample_rooms:
            data_manager.add_room(room["name"], room["capacity"])
        
        for cls in sample_classes:
            data_manager.add_class(cls["name"], cls["size"])
        
        for course in sample_courses:
            data_manager.add_course(
                course["name"],
                course["teacher"],
                course["class"],
                course["duration"],
                course["frequency"]
            )
        
        # Update session state
        st.session_state.teachers = data_manager.get_teachers()
        st.session_state.rooms = data_manager.get_rooms()
        st.session_state.classes = data_manager.get_classes()
        st.session_state.courses = data_manager.get_courses()
        
        st.success("Sample data loaded successfully!")
        st.rerun()

# Generate Schedule Section
elif section == "Generate Schedule":
    st.header("Generate Schedule")
    
    if not st.session_state.courses or not st.session_state.rooms or not st.session_state.teachers or not st.session_state.classes:
        st.warning("Please add teachers, rooms, classes, and courses before generating a schedule.")
        st.info("Go to the 'Input Data' section to add the required data.")
    else:
        st.subheader("Schedule Generation Options")
        
        with st.form("schedule_options_form"):
            start_time = st.time_input("School day start time", value=pd.to_datetime("08:00").time())
            end_time = st.time_input("School day end time", value=pd.to_datetime("15:15").time())
            period_length = st.slider("Period length (minutes)", min_value=30, max_value=120, value=50, step=5)
            break_length = st.slider("Break between periods (minutes)", min_value=5, max_value=30, value=10, step=5)
            lunch_period = st.selectbox("Lunch period", options=["No lunch", "After period 3", "After period 4"])
            lunch_duration = st.slider("Lunch duration (minutes)", min_value=20, max_value=60, value=30, step=5, disabled=lunch_period=="No lunch")
            
            generate_button = st.form_submit_button("Generate Schedule")
            
            if generate_button:
                with st.spinner("Generating schedule..."):
                    # Configure the schedule generator
                    scheduler = ScheduleGenerator(
                        teachers=st.session_state.teachers,
                        rooms=st.session_state.rooms,
                        classes=st.session_state.classes,
                        courses=st.session_state.courses,
                        start_time=start_time,
                        end_time=end_time,
                        period_length=period_length,
                        break_length=break_length,
                        lunch_period=lunch_period,
                        lunch_duration=lunch_duration
                    )
                    
                    # Generate the schedule
                    schedule, conflicts = scheduler.generate_schedule()
                    
                    # Update session state
                    st.session_state.schedule = schedule
                    st.session_state.conflicts = conflicts
                    
                    if conflicts:
                        st.error(f"Schedule generated with {len(conflicts)} conflicts. Please see the 'Manage Conflicts' section.")
                    else:
                        st.success("Schedule generated successfully with no conflicts!")

        if st.session_state.schedule is not None:
            st.subheader("Generated Schedule Summary")
            
            # Display a summary of the generated schedule
            n_classes = len(set([item['class'] for item in st.session_state.schedule]))
            n_courses = len(set([(item['class'], item['course']) for item in st.session_state.schedule]))
            n_slots = len(st.session_state.schedule)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Classes Scheduled", n_classes)
            col2.metric("Courses Assigned", n_courses)
            col3.metric("Total Time Slots", n_slots)
            
            st.info("Go to the 'View Schedule' section to see the detailed timetable.")

# View Schedule Section
elif section == "View Schedule":
    st.header("View Schedule")
    
    if st.session_state.schedule is None:
        st.warning("No schedule has been generated yet.")
        st.info("Go to the 'Generate Schedule' section to create a schedule.")
    else:
        # Create view options
        st.subheader("View Options")
        
        view_col1, view_col2 = st.columns(2)
        
        with view_col1:
            view_mode = st.radio("View by:", ["Class", "Teacher", "Room"])
            st.session_state.view_mode = view_mode
        
        with view_col2:
            if view_mode == "Class":
                selected_filter = st.selectbox(
                    "Select Class:",
                    options=[c['name'] for c in st.session_state.classes]
                )
            elif view_mode == "Teacher":
                selected_filter = st.selectbox(
                    "Select Teacher:",
                    options=[t['name'] for t in st.session_state.teachers]
                )
            else:  # Room view
                selected_filter = st.selectbox(
                    "Select Room:",
                    options=[r['name'] for r in st.session_state.rooms]
                )
        
        # Create visualizer
        visualizer = ScheduleVisualizer(st.session_state.schedule)
        
        # Display the schedule
        st.subheader(f"Schedule by {view_mode}: {selected_filter}")
        
        if view_mode == "Class":
            fig = visualizer.generate_class_schedule(selected_filter)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show detailed table
            detailed_schedule = visualizer.get_class_schedule_data(selected_filter)
            if not detailed_schedule.empty:
                st.subheader("Detailed Schedule")
                st.dataframe(detailed_schedule, use_container_width=True)
            else:
                st.info(f"No schedule data available for class {selected_filter}")
                
        elif view_mode == "Teacher":
            fig = visualizer.generate_teacher_schedule(selected_filter)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show detailed table
            detailed_schedule = visualizer.get_teacher_schedule_data(selected_filter)
            if not detailed_schedule.empty:
                st.subheader("Detailed Schedule")
                st.dataframe(detailed_schedule, use_container_width=True)
            else:
                st.info(f"No schedule data available for teacher {selected_filter}")
                
        else:  # Room view
            fig = visualizer.generate_room_schedule(selected_filter)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show detailed table
            detailed_schedule = visualizer.get_room_schedule_data(selected_filter)
            if not detailed_schedule.empty:
                st.subheader("Detailed Schedule")
                st.dataframe(detailed_schedule, use_container_width=True)
            else:
                st.info(f"No schedule data available for room {selected_filter}")
        
        # Export options
        st.subheader("Export Options")
        
        if st.button("Export Schedule to CSV"):
            full_schedule_df = visualizer.get_full_schedule_data()
            csv = full_schedule_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="class_schedule.csv",
                mime="text/csv"
            )

# Manage Conflicts Section
elif section == "Manage Conflicts":
    st.header("Manage Conflicts")
    
    if st.session_state.schedule is None:
        st.warning("No schedule has been generated yet.")
        st.info("Go to the 'Generate Schedule' section to create a schedule.")
    elif not st.session_state.conflicts:
        st.success("No conflicts detected in the current schedule.")
    else:
        st.warning(f"There are {len(st.session_state.conflicts)} conflicts in the current schedule.")
        
        # Display conflicts
        conflict_data = []
        for conflict in st.session_state.conflicts:
            conflict_data.append({
                "Type": conflict["type"],
                "Day": conflict["day"],
                "Time": conflict["time"],
                "Description": conflict["description"]
            })
        
        conflict_df = pd.DataFrame(conflict_data)
        st.dataframe(conflict_df, use_container_width=True)
        
        # Conflict resolution
        st.subheader("Resolve Conflicts")
        
        conflict_to_resolve = st.selectbox(
            "Select conflict to resolve:",
            options=[f"{c['type']} - {c['day']} {c['time']} - {c['description']}" for c in st.session_state.conflicts],
            index=0
        )
        
        selected_conflict_idx = [f"{c['type']} - {c['day']} {c['time']} - {c['description']}" for c in st.session_state.conflicts].index(conflict_to_resolve)
        selected_conflict = st.session_state.conflicts[selected_conflict_idx]
        
        st.subheader("Resolution Options")
        
        resolution_type = st.radio(
            "Resolution approach:",
            ["Reschedule", "Change room", "Change teacher"]
        )
        
        if resolution_type == "Reschedule":
            new_day = st.selectbox("New day:", options=DAYS)
            new_time = st.selectbox("New time:", options=TIME_SLOTS)
            
            if st.button("Apply Change"):
                st.info("This would update the schedule with the new time slot.")
                st.warning("Manual conflict resolution is not fully implemented. Please regenerate the schedule.")
                
        elif resolution_type == "Change room":
            new_room = st.selectbox(
                "New room:", 
                options=[r['name'] for r in st.session_state.rooms]
            )
            
            if st.button("Apply Change"):
                st.info("This would update the room assignment for the conflicting course.")
                st.warning("Manual conflict resolution is not fully implemented. Please regenerate the schedule.")
                
        elif resolution_type == "Change teacher":
            new_teacher = st.selectbox(
                "New teacher:", 
                options=[t['name'] for t in st.session_state.teachers]
            )
            
            if st.button("Apply Change"):
                st.info("This would update the teacher assignment for the conflicting course.")
                st.warning("Manual conflict resolution is not fully implemented. Please regenerate the schedule.")
        
        # Option to regenerate schedule
        st.subheader("Regenerate Schedule")
        if st.button("Regenerate Schedule"):
            st.info("This would regenerate the schedule with updated constraints.")
            st.warning("Please go to the 'Generate Schedule' section to regenerate the schedule.")
