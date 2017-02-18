
class Assignment():
    """
    A label comprising a timeslot, a room and an instructor that can
    be assigned to a a lecture node.
    """
    def __init__(self, instructor, room, timeslot):
        """
        Constructor
        """
        self._instructor = instructor
        self._room = room
        self._timeslot = timeslot

    @property        
    def room(self):
        return self._room    
    
    @property        
    def instructor(self):
        return self._instructor  
    
    @property        
    def timeslot(self):
        return self._timeslot  
        
    def satisfies_constraints(self, lecture):
        """
        Check whether the assignment can be used for the lecture.
        """
        satisfies = (self._instructor.can_teach(lecture) and 
                    self._room.can_be_used_for(lecture))
        return satisfies
    
    def overlaps_instructor_at_time(self, other):
        """
        Check whether another assignment uses the same instructor at the same time.
        """
        return self._instructor == other._instructor and self._timeslot == other._timeslot 
    
    def overlaps_room_at_time(self, other):
        """
        Check whether another assignment uses the same room at the same time.
        """
        return self._room == other._room and self._timeslot == other._timeslot 
    
    def __eq__(self, other):
        
        if not isinstance(other, Assignment):
            return False
        return (self._instructor == other._instructor and
                self._room == other._room and
                self._timeslot == other._timeslot)
        
    def __hash__(self):
        """Implement hash so objects can be used in sets."""
        return hash(hash(self._instructor) + hash(self._room) + hash(self._timeslot))
        
    def __repr__(self):
        
        return '<Assignment: {}, {}, {}>'.format(
            self._instructor, self._room, self._timeslot)
    
    def __str__(self):
        
        return 'Assignment: {}, {}, {}'.format(
            self._instructor, self._room, self._timeslot)    
        