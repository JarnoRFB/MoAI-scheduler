from scheduler import Timeslot, Room, Instructor
from scheduler.assignment import Assignment
from scheduler.exceptions import ImpossibleAssignments
from scheduler.helper import format_for_print
from copy import deepcopy
import warnings
from collections import Counter
from pandas import DataFrame


class Timetable():
    """
    Contains all lectures and assignments. Can fit a schedule 
    according to constraints. 
    """
    def __init__(self, lecture_list, instructor_list, 
                 room_list, timeslot_list, max_lectures_per_instructor):
        """
        Constructor
        """
        self._lectures = self._construct_lectures(lecture_list)
        self._instructors = self._construct_instructors(instructor_list)
        self._rooms = self._construct_rooms(room_list)
        self._timeslots = self._construct_timeslots(timeslot_list)
        self._scheduled = False
        self._schedule = {}
        self._schedule_df = None
        self._assignments = self._construct_assignments()
        self._max_lectures_per_instructor = max_lectures_per_instructor
    

    def find_schedule(self):
        """Schedule the timetable."""
        # Use a dictionary to map an assignment to each lecture.
        schedule = {lecture: None for lecture in self._lectures}
        # Keep track of what can be assigned in a set.
        assignable = set(self._assignments)
    
        try:
            final_schedule = self._assign_values(schedule, assignable)
            self._scheduled = True
            self._schedule = final_schedule
            self._schedule_df = self._save_schedule_in_dataframe()
        except ImpossibleAssignments:
            raise ImpossibleAssignments( 'Unable to find schedule without violating constraints.' )
             
        
    def _assign_values(self, schedule, assignable):
        """
        Assign an unassigned variable and traverse the search tree further.
        
        Args:
            schedule (dict): The partially constructed schedule.
            assignable (set): The values that have not yet been assigned.
        """
        # base case 
        if None not in schedule.values():
            return schedule
        
        schedule = deepcopy(schedule)
        assignable = deepcopy(assignable)
        unassigned_vars = (lecture for lecture, assignment in schedule.items() 
                           if assignment is None)
        for lecture in unassigned_vars:
            for assignment in assignable:
                if assignment.satisfies_constraints(lecture):
                    schedule[lecture] = assignment
                    # Check for global constraints.
                    if self._satisfies_higher_order_constraints(schedule):
                        
                        left_assignables = deepcopy(assignable)
                        left_assignables.remove(assignment)
                        try:
                            # Recursively call the function to traverse the search tree.
                            return self._assign_values(schedule, left_assignables)
                        except ImpossibleAssignments:
                            continue
                    else:
                        # Remove invalid assignment if higher order constraints are violated.
                        schedule[lecture] = None
                        
        # No assignment could be found for any lecture at this point.
        raise ImpossibleAssignments('No assignment could be found for any lecture at this point.')
    
        
    def _satisfies_higher_order_constraints(self, schedule):
        """Check for satisfaction of higher order constraints."""
        return (self._satisfies_maximal_number_of_instructor(schedule) and
                self._satisfies_instructor_double_occupancy(schedule) and
                self._satisfies_room_double_occupancy(schedule))
        
    def _satisfies_instructor_double_occupancy(self, schedule):
        """No room can be used twice at the same timeslot."""
        instructor_timeslot_counts = Counter([(assignment.instructor, assignment.timeslot) 
                                      for assignment in schedule.values() 
                                      if assignment is not None])
#         print(instructor_timeslot_counts)
        for count in instructor_timeslot_counts.values():
            if count > 1:
                return False
        return True     
                            
    def _satisfies_room_double_occupancy(self, schedule):
        """No instructor can give two lectures at the same time."""
        room_timeslot_counts = Counter([(assignment.room, assignment.timeslot) 
                                      for assignment in schedule.values()
                                      if assignment is not None])
        for count in room_timeslot_counts.values():
            if count > 1:
                return False
        return True                        
    
    def _satisfies_maximal_number_of_instructor(self, schedule):
        """Check whether an instructor gives too many lectures."""
        instructor_counts = Counter([assignment.instructor 
                                      for assignment in schedule.values()
                                      if assignment is not None])
        
        for count in instructor_counts.values():
            if count > self._max_lectures_per_instructor:
                return False
        return True    
        
    def _save_schedule_in_dataframe(self):
        
        schedule_ll = []
        for lecture, assignment in self._schedule.items():
            schedule_ll.append([str(lecture), str(assignment.timeslot), str(assignment.instructor), str(assignment.room)])
        df = DataFrame(schedule_ll, columns=['Lecture', 'Time', 'Instructor', 'Room'])
        df.sort_values('Time', inplace=True)
        return df
        
        
    def _construct_assignments(self):
        """
        Construct possible combinations of instructor, room and timeslot.
        """
        assignments = []
        for instructor in self._instructors:
            for room in self._rooms:
                for timeslot in self._timeslots:
                    if (instructor.can_teach_at(timeslot) and 
                        room.can_be_used_at(timeslot)):
                        assignments.append(Assignment(instructor, room, timeslot))
        return assignments
        
    
    def _construct_lectures(self, lecture_list):
        """Construct lectures from list specification."""
        lectures = []
        for name in lecture_list:
            if name not in lectures:
                lectures.append(name)
            else:
                warnings.warn('Lecture %s specified more than once.' % name)
                
        return lectures
                
        
    def _construct_instructors(self, instructor_list):
        """Construct instructors from list specification."""
        instructors = []
        for instructor_spec in instructor_list:
            name = instructor_spec[0]
            lectures = self._construct_lectures(instructor_spec[1])
            timeslots = self._construct_constraint_timeslots(
                instructor_spec[2], instructor_spec[3])
            instructors.append(Instructor(name, lectures, timeslots))
        return instructors
            
            
    def _construct_rooms(self, room_list):
        """Construct rooms from list specification."""
        rooms = []
        for room_spec in room_list:
            lectures = self._construct_lectures(room_spec[1])
            timeslots = self._construct_constraint_timeslots(
                room_spec[2], room_spec[3])
            rooms.append(Room(room_spec[0], lectures, timeslots))
        return rooms
    
    def _construct_timeslots(self, timeslot_list):
        """Construct timeslots from list specification."""
        timeslots = []
        for timeslot_spec in timeslot_list:
            day, start_end = timeslot_spec.split()
            start, end = start_end.split('-')
            timeslots.append(Timeslot(day, start, end))
        return timeslots
            
            
    def _construct_constraint_timeslots(self, days, times):
        """
        Construct timeslots from the instructor or room specification.
        """
        timeslots = []
        # An empty list is equal to no restriction.
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] if not days else days
        times = ['10-12', '12-14', '14-16'] if not times else times
        for day in days:
            for start_end in times:
                start, end = start_end.split('-')
                timeslots.append(Timeslot(day, start, end))
                
        return timeslots
        
            
        
    def __repr__(self):
        return '<Timetable {}'.format(vars(self))
        
    def __str__(self):
        
        if self._scheduled:
            return format_for_print(self._schedule_df)
#             return str(self._schedule_df)
                
        
        else:
            return "Unscheduled timetable"
            
            

        
        
        