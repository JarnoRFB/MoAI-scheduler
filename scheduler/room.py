
class Room():
    """
    A room to give lectures in.
    """
    def __init__(self, number, lectures, timeslots):
        """
        Constructor
        """
        self.number = number
        self._lectures = lectures
        self._timeslots = timeslots
        
    def can_be_used_for(self, lecture):
        """
        Is the lecture be given in the room?
        """ 
        return lecture in self._lectures
    
    def can_be_used_at(self, timeslot):
        """
        Can the room be used at a certain timeslot?
        """ 
        return timeslot in self._timeslots    
    
    def __repr__(self):
        return '<Room No.{}>'.format(self.number)
    
    def __str__(self):
        return 'No.{}'.format(self.number)
    
    def __eq__(self, other):
        return self.number == other.number
    
    def __hash__(self):
        return hash(self.number)