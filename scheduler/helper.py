"""
Some helper functions used throughout the scheduler.
"""
from prettytable import PrettyTable
    
def format_for_print(df):    
    table = PrettyTable(list(df.columns))
    for row in df.itertuples():
        table.add_row(row[1:])
    return str(table)













