

class Timeslot():
    """
    A timeslot a lecture can be held at.
    """
    def __init__(self, day, start, end):
        
        self._day = day
        self._start = start
        self._end = end
        
    def __repr__(self):
        return '<Timeslot {} {}-{}>'.format(
            self._day, self._start, self._end)
    
    def __str__(self):
        return '{} {}-{}'.format(
            self._day, self._start, self._end)
        
    def __hash__(self):
        return hash(self._day + self._start + self._end)
    
    def __eq__(self, other):
        return (self._day == other._day and
                self._start == other._start and
                self._end == other._end)