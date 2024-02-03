# Place code below to do the analysis part of the assignment.
# -*- coding: utf-8 -*-

"""
analyze.py - print mean temperature anomaly
"""

import csv
import os.path

YEAR_INDEX = "Year"
ANN_MEAN_INDEX = "J-D"

def _display_periodic_avg(
    reader, 
    *, 
    period: int = 10, 
    print_last: bool = True
) -> None:
    """
    Display average temperature anomaly over a period of years.

    Parameters
    ----------
    reader: CSV reader that contains the temperature anomaly file
    period: int, the period the mean is calculated, default 10
    print_last: bool, whether the mean of the last interval should
        be printed if it is less than the period
    
    Raises
    ------
    ValueError : iterator of the ``reader`` is empty.
    """
    # Stores the first year and last year of an interval.
    year_range: dict[str:int] = dict()
    anomaly_sum = 0
    
    for row in reader:
        this_year = int(row[YEAR_INDEX])
        curr_anomaly = float(row[ANN_MEAN_INDEX])

        # Begin a new decade.
        if not year_range:
            year_range["start"] = this_year

        anomaly_sum += curr_anomaly
        year_range["end"] = this_year

        if this_year - year_range['start'] + 1 == period:
            print(f"{year_range['start']} to {year_range['end']}: the average "
                  + f"temperature anomaly is {anomaly_sum / period} degrees.")
            
            anomaly_sum = 0
            year_range.clear()

    # Process unreported value.
    if year_range and print_last:
        avg = anomaly_sum / (year_range['end'] - year_range['start'] + 1)
        print(f"{year_range['start']} to {year_range['end']}: "
              + f"the average temperature anomaly is {avg} degrees.")
    
    return None


def main():
    # Setup file directory.
    root = os.path.dirname(__file__)
    data_path = os.path.join(root, "data/clean_data.csv")

    # Read data and output average.
    with open(data_path, "r") as data:
        reader = csv.DictReader(data, delimiter=",")
        _display_periodic_avg(reader)
            

if __name__ == "__main__":
    main()