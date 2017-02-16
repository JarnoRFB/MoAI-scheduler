class Lecture():
    
    
    def __init__(self, name):
        
        self._name = name
#         self._assignment = None
        
#     def assign(self, assignment):
#         """
#         Assign an assignment if it does not violate any constraints.
#         """
#         if not assignment.violates_constraints(self):
#             self._assignment = assignment
        
    def __repr__(self):
        return '<{} Lecture>'.format(self._name)
    
    def __str__(self):
        return '{} Lecture'.format(self._name)
    
    def __eq__(self, other):
        return self._name == other._name
    
    def __hash__(self):
        return hash(self._name)