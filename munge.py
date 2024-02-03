# Place code below to do the munging part of this assignment.
# -*- coding: utf-8 -*-

"""
munge.py - clean up fwf/write CSV files
"""

import re
import os.path

NO_RESTRICTION = 0
TO_FARENHEIT_COEFFICIENT = 1.8


def write_csv(
    destination: str, 
    data: list[list[str]], 
    *, 
    encoding: str = "utf-8", 
    overwrite: bool = False
) -> None: 
    """
    Write data to given directory as CSV file. Discard repeated headers and 
    rows that are not in fwf format.

    Parameters
    ----------
    destination : str, path to where data to be saved, a URL, default ``""``
        String, the parsed data will be written to desired. If empty, 
        return the parsed data. Create a file if it does not exist. 
    data : list of list of str
        A list of string lists with each of them representing a row of the 
        CSV file (the first row is the header).
    encoding : str, default utf-8
        String, the encoding the data should use.
    overwrite : bool, default ``False``.
        Boolean, overwrite the destination file if true. Otherwise, 
        raise ``FileExistsError``.

    Raises
    ------
    FileExistsError : if the file specified ``destination`` already exists and
        ``overwrite`` is ``False``.
    """
    # Check if can write.
    if not overwrite and os.path.isfile(path=destination):
        raise FileExistsError(f"{destination} already exists")
    
    # Write to destination.
    with open(destination, "w", encoding=encoding) as file:
        for row in data:
            file.write(",".join(row) + "\n")

def _is_postive_integer(x: int) -> bool:
    """Return if input is positive integer."""
    return type(x) == int and x > 0


def parse_fixed_width_data(
    path: str, 
    *,
    start: int, 
    end: int, 
    col_len: int | None = None, 
    encoding: str = "utf-8", 
    destination: str = "", 
    overwrite: bool = False
) -> (list[list[str]] | None):
    """
    Parse a fixed-width file at a given directory.

    Parameters
    ----------
    path : str, path to the data, a URL
        String, the directory of the file. For example, 
        ``ocean_temp_data.fwf``.
    start: int, header line of the actual data
        The line number of the first header of the data file.
    end: int, last line of the actual data
        The line number of the last line of the data file.
    col_len: int, number of columns, optional
        Number of columns in the desired data. Discard extra column if 
        original data has more.
    encoding : str, default utf-8
        String, the encoding the file used.
    destination : str, path to where data to be saved, a URL, default ``""``
        String, the parsed data will be written to desired. If empty, 
        return the parsed data. Create a file if it does not exist. 
    overwrite : bool, default ``False``.
        Boolean, overwrite the destination file if true. Otherwise, 
        raise ``FileExistsError``.
    
    Returns
    -------
    list[list[str]] or ``None`` 
        Return a list with the each element is 
        a list representing a row of the original header and data (the 
        first row is the header and all other rows are rows of data).
        Return ``None`` if `destination` is specified.

    Raises
    ------
    ValueError : if one or more inputs invalid.
    FileNotFoundError : if source file specified by ``path`` does not exist.
    FileExistsError : if the file specified ``destination`` already exists and
        ``overwrite`` is ``False``.
    """
    # Check input 'start' and 'end'.
    if not _is_postive_integer(start):
        raise ValueError(f"'start' ({start}) must be a positive integer")
    if not _is_postive_integer(end):
        raise ValueError(f"'end' ({end}) must be a positive integer")
    if start > end:
        raise ValueError(f"'start' ({start}) must be less than or \
                         equal to 'end' ({end})")
    # Check 'col_len'.
    if col_len is not None \
    and not _is_postive_integer(col_len) \
    and col_len != 0:
        raise ValueError(f"'col_len' ({col_len}) must be an integer at least 0")

    # Setup split limit for extracting data.
    maxsplit: int = col_len if col_len else NO_RESTRICTION

    with open(path, "r", encoding=encoding) as data_file:
        # Skip lines before start.
        for _ in range(start - 1):
            data_file.readline()
        
        # Create data container.
        data: list[list[str]] = []

        # Parse data between start and end lines, inclusive.
        header: list[str] | None = None
        for row_number in range(start, end + 1):
            source_row = re.split("[\s]+", data_file.readline(), 
                           maxsplit=maxsplit)
            data_row: list[str] = source_row[:min(len(source_row), maxsplit)]
            
            # Check if 'data_row' inconsisitent with CSV format.
            if header and len(data_row) != len(header):
                continue
            # Check if 'data_row' is header.
            if data_row == header:
                continue
            
            if row_number == start:
                header = data_row
            data.append(data_row)
    
    if not destination:
        return data

    write_csv(destination, data, encoding=encoding, overwrite=overwrite)
    return None


def _to_farenheit(
    data: list[list[str]], 
    *, 
    start: (int, int) = (0, 0), 
    end: [any, any] = [None, None]
) -> None:
    """
    Convert a rectangle range of entries of a m * n list to 
    Farenheit temperature.
    
    Parameters
    ----------
    data: 2d list of str, the data that contain the entries to be converted
    start: tuple of int, row and column indices of the upleft entry of 
        the region to be converted
    end: tuple of int, row and column indices of the right down entry of 
        the last entry of the region
    """
    if len(data) == 0 or len(data[0]) == 0:
        return None
    
    end[0] = end[0] if end[0] else len(data)
    end[1] = end[1] if end[1] else len(data[0][0])

    for row_index in range(start[0], end[1]):
        for col_index in range(start[1], end[1]):
            entry = data[row_index][col_index]
            if not entry.isnumeric:
                continue
            val = float(entry) * TO_FARENHEIT_COEFFICIENT
            data[row_index][col_index] = f"%.1f" % val
    
    return None


def main():
    # Set file directory.
    root = os.path.dirname(__file__)
    data_path = os.path.join(root, "data/ocean_temp_data.fwf")
    target_path = os.path.join(root, "data/clean_data.csv")

    # Parse and convert data.
    data: list[list[str]] = parse_fixed_width_data(data_path, 
                           start=8, end=166, col_len=19)
    _to_farenheit(data, start=(1, 1))
    
    # Fix missing value.
    djf_10 = sum([float(data[c][-4]) for c in range(2, 12)])
    data[1][-4] = f"%.1f" % (djf_10 % 10) # DJF 1880

    d_n_sum = sum([float(data[1][r]) for r in range(-4, 0, 1)])
    data[1][-5] = f"%.1f" % (d_n_sum % 4) # D-N 1880

    # Save data.
    write_csv(target_path, data, encoding="utf-8", overwrite=True)
    

if __name__ == "__main__":
    main()