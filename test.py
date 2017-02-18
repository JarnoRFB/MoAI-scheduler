"""A simple scheduling problem for demonstrating the functionality of the scheduler."""
from scheduler import Timetable
from scheduler.exceptions import ImpossibleAssignments

# name
lecture_list = [
    'Methods of AI',
    'Neuroinformatics',
    'Human-Computer Interfaces',
]
# name lectures[] days[] times[]
instructor_list = [
    ['Kühnberger', ['Methods of AI', 'Human-Computer Interfaces', 'Neuroinformatics'],
        ['Mon', 'Wed'], []],
    ['Potyka', ['Methods of AI'], [], ['10-12', '12-14']]
]
# number lectures[] days[] times[]
room_list = [
    [1, ['Methods of AI'], ['Mon', 'Thu'], []],
    [2, ['Human-Computer Interfaces', 'Neuroinformatics'], ['Mon', 'Thu'], []],
]
# day start-end
timeslot_list = [
    'Mon 8-10',
    'Mon 10-12',
    'Mon 12-14',
    'Thu 8-10',
    'Thu 10-12',
    'Thu 12-14',
]


timetable = Timetable(lecture_list, instructor_list, room_list, timeslot_list,
                      max_lectures_per_instructor=3)


try:
    timetable.find_schedule()
    print(timetable)
except ImpossibleAssignments as e:
    print(e)