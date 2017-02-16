
class Instructor():
    """
    A instructor can give certain lectures at certain times.
    """
    def __init__(self, name, lectures, timeslots):
        """
        Constructor
        """
        self._name = name
        self._lectures = lectures
        self._timeslots = timeslots
        
    def can_teach(self, lecture):
        """
        Is the instructor able to give the lecture.
        """ 
        return lecture in self._lectures
    
    def can_teach_at(self, timeslot):
        """
        Is the instructor able to teach at a certain timeslot.
        """
        return timeslot in self._timeslots
    
    def __repr__(self):
        return '<Instructor  {}>'.format(self._name)
    
    def __str__(self):
        return '{}'.format(self._name)
    
    def __eq__(self, other):
        return self._name == other._name 
    
    def __hash__(self):
        return hash(self._name)