from scheduler import Timeslot, Room, Instructor
from scheduler.assignment import Assignment
from scheduler.exceptions import ImpossibleAssignments
from scheduler.helper import format_for_print, sort_dict_by_mrv
from copy import deepcopy
import warnings
from collections import Counter
from pandas import DataFrame
import time
import operator


class Timetable():
    """
    Contains all lectures and assignments. Can fit a schedule 
    according to constraints. 
    """
    def __init__(self, lecture_list, instructor_list, 
                 room_list, timeslot_list, max_lectures_per_instructor,
                 print_intermediate_results=False):
        """
        Constructor
        """
        self._lectures = self._construct_lectures(lecture_list)
        self._instructors = self._construct_instructors(instructor_list)
        self._rooms = self._construct_rooms(room_list)
        self._timeslots = self._construct_timeslots(timeslot_list)
        self.print_intermediate_results = print_intermediate_results
        self._scheduled = False
        self._schedule = {}
        self._schedule_df = None
        self._assignments = self._construct_assignments()
        self._max_lectures_per_instructor = max_lectures_per_instructor
 
    
# ----------------------- methods for scheduling -----------------------

    def find_schedule(self):
        """Schedule the timetable."""
        # Use a dictionary to map an assignment to each lecture.
        schedule = self._init_schedule_dict()

        try:
            final_schedule = self._assign_values(schedule)
            self._scheduled = True
            self._schedule = final_schedule
            self._schedule_df = self._save_schedule_in_dataframe()
        except ImpossibleAssignments:
            raise ImpossibleAssignments( 'Unable to find schedule without violating constraints.' )
             
        
    def _assign_values(self, schedule):
        """
        Assign an unassigned variable and traverse the search tree further.
        
        Args:
            schedule (dict): The partially constructed schedule.
            assignable (set): The values that have not yet been assigned.
        """
        # base case 
        if self._schedule_complete(schedule):
            return schedule
        
        if self.print_intermediate_results:
            # Print the current state of the scheduler every ten seconds.
            if int(time.time()) % 10 == 0:
                print('\n')
                print(schedule)
                n_assigned = 0
                for a in schedule.values():
                    if not isinstance(a, set): n_assigned += 1
                print('assigned: ', n_assigned)
                print(list(self._get_unassigned_vars(schedule)))

        schedule = deepcopy(schedule)
        
        # Iterate over unassigned variables.
        for lecture in self._get_unassigned_vars(schedule, sort=True):
            # Iterate over domain.
            domain = deepcopy(schedule[lecture])
            for assignment in self._sort_by_lcv(domain, lecture, schedule):
                schedule[lecture] = assignment
                # Propagate constraints.
                try:
                    reduced_domains_schedule = self._reduce_domains(deepcopy(schedule), assignment)
                    reduced_domains_schedule = self._resolve_small_domains(reduced_domains_schedule)
                    # Recursively call the function to traverse the search tree.
                    return self._assign_values(reduced_domains_schedule)
                except ImpossibleAssignments:
                    # Remove invalid assignment and restore domain if higher order constraints cause 
                    # domain to become empty.
                    schedule[lecture] = domain
                    continue
                

                        
        # No assignment could be found for any lecture at this point.
        raise ImpossibleAssignments('No assignment could be found for any lecture at this point.')
    
    def _reduce_domains(self, schedule, new_assignment):
        """Reduce domains by propagating constraints.""" 
        busy_instructors = self._get_busy_instructors(schedule)
        
        for lecture in self._get_unassigned_vars(schedule):
            # Remove the newly assigned value from any other domain.
            schedule[lecture].discard(new_assignment)
            # Check whether the removal makes the domain empty.
            if not schedule[lecture]:
                raise ImpossibleAssignments('Assignment leads to inconsistencies.')
            domain = deepcopy(schedule[lecture])
            
            for assignment in domain:
                # Remove values from other domains if they cointain the same instructor at the same time.
                # Remove values from other domains if they cointain the same room at the same time.
                # Remove values from other domains if they cointain an instructor that 
                # already gives the maximun number of lectures.
                if (new_assignment.overlaps_instructor_at_time(assignment) or
                    new_assignment.overlaps_room_at_time(assignment) or
                    assignment.instructor in busy_instructors):
                    schedule[lecture].discard(assignment)
                    # Check whether the removal makes the domain empty.
                    if not schedule[lecture]:
                        raise ImpossibleAssignments('Assignment leads to inconsistencies.')
        
        return schedule

    def _resolve_small_domains(self, schedule):
        """
        Assign domains with a cardinality of one and reduce domains further.
        """
        while(self._contains_small_domains(schedule)):
            for lecture in self._get_unassigned_vars(schedule):
                if len(schedule[lecture]) == 1:
                    assignment = schedule[lecture].pop()
                    schedule[lecture] = assignment
                    schedule = self._reduce_domains(schedule, assignment)

        return schedule
        
    def _get_busy_instructors(self, schedule):
        """Check whether an instructor gives too many lectures."""
        instructor_counts = Counter([assignment.instructor 
                                      for assignment in schedule.values()
                                      if not isinstance(assignment, set)])
        busy_instructors = set()
        
        for instructor, count in instructor_counts.items():
            if count > self._max_lectures_per_instructor:
                busy_instructors.add(instructor)
        return busy_instructors    
        
    def _init_schedule_dict(self):
        """
        Initialize schedule where each lecture is mapped to all possible assignments.
        """
        schedule = {}
        
        for lecture in self._lectures:
            domain = set()
            for assignment in self._assignments:
                if assignment.satisfies_constraints(lecture):
                    domain.add(assignment)
            schedule[lecture] = domain
        return schedule
    
    def _schedule_complete(self, schedule):
        """Check whether there are still unassigned variables in the schedule."""
        for assignment in schedule.values():
            if isinstance(assignment, set):
                return False
        return True
    
    def _get_unassigned_vars(self, schedule, sort=False):
        """Get all variables that have not yet been assigned a value."""
        if sorted:
            schedule = sort_dict_by_mrv(schedule)
        
        unassigned_lectures = []
        
        for lecture, assignment in schedule.items():
            if isinstance(assignment, set):
                unassigned_lectures.append(lecture)
        return unassigned_lectures
    
#     def _sort_by_lcv(self, domain, lecture, schedule):
#         """Sort the values in a domain according to least-constraining-value heuristic."""
#         schedule = deepcopy(schedule)
#         max_total_domain_cardinality = -float('inf')
#         least_constraining_value = None
#         for value in domain:
#             # Assign value to lecture and reduce the other domains.
#             try:
#                 assigned_schedule = deepcopy(schedule)
#                 assigned_schedule[lecture] = value
#                 total_domain_cardinality = self._reduce_domains(assigned_schedule, value)
#                 if total_domain_cardinality > max_total_domain_cardinality:
#                     least_constraining_value = value
#                     max_total_domain_cardinality = total_domain_cardinality
#             except ImpossibleAssignments:
#                 continue
    
    def _sort_by_lcv(self, domain, lecture, schedule):
        """Sort the values in a domain according to least-constraining-value heuristic."""
        schedule = deepcopy(schedule)
        value_cardinality = {value: 0 for value in domain}
        for value in domain:
            # Assign value to lecture and reduce the other domains.
            try:
                assigned_schedule = deepcopy(schedule)
                assigned_schedule[lecture] = value
                value_cardinality[value] = self._get_number_of_remaining_values(
                    self._reduce_domains(assigned_schedule, value)
                )
            except ImpossibleAssignments:
                continue
            
        sorted_tuples = sorted(value_cardinality.items(), key=operator.itemgetter(1), reverse=True)
        sorted_values = (tup[0] for tup in sorted_tuples)
        return sorted_values
            
            
    def _get_number_of_remaining_values(self, schedule):
        """Get the number of remaining values in all domains."""
        n_total = 0
        for lecture in self._get_unassigned_vars(schedule):
            n_total += len(schedule[lecture])
        
        return n_total
    
    def _contains_small_domains(self, schedule):
        """Check whether the CSP contains a domain of cardinality one."""
        for assignment in schedule.values():
            if isinstance(assignment, set) and len(assignment) == 1:
                return True
        return False
        
    def _save_schedule_in_dataframe(self):
        """Save the schedule dictionary to a pandas dataframe."""
        schedule_ll = []
        
        for lecture, assignment in self._schedule.items():
            schedule_ll.append([str(lecture), str(assignment.timeslot), str(assignment.instructor), str(assignment.room)])
        df = DataFrame(schedule_ll, columns=['Lecture', 'Time', 'Instructor', 'Room'])
        df.sort_values('Time', inplace=True)
        return df


# ----------------- helper methods for initialization ------------------
     
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
        
        
# --------------------------- dunder methods ---------------------------
       
    def __repr__(self):
        return '<Timetable {}'.format(vars(self))
        
    def __str__(self):
        if self._scheduled:
            return format_for_print(self._schedule_df)
        else:
            return "Unscheduled timetable"
            
            

        
        
        