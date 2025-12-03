"""
Seat Allocation Module for GIC Cinemas

Implements seat selection algorithms:
1. Default selection - furthest row, middle columns, overflow forward
2. Custom position - from specified seat, fill right, overflow with default rules
"""

import re
import string
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from models import Seat, Movie


def get_middle_start_column(seats_per_row: int, num_tickets: int) -> int:
    """
    Calculate the starting column for centered seat allocation.

    For a row with N seats and requesting T tickets:
    - Find the middle point of the row
    - Calculate starting position so tickets are centered

    Args:
        seats_per_row: Total seats in a row
        num_tickets: Number of tickets to allocate

    Returns:
        Starting column number (1-indexed)
    """
    if num_tickets >= seats_per_row:
        return 1

    # Calculate center position
    # For 10 seats: center is between 5 and 6, so middle point is 5.5
    # For 5 seats: center is 3
    center = (seats_per_row + 1) / 2

    # Calculate offset to center the tickets
    # For 2 tickets: offset = 1, so start at center - 0.5 = 5 (for 10 seats)
    # For 3 tickets: offset = 1.5, so start at center - 1 = 4.5 -> 4 (for 10 seats)
    half_tickets = num_tickets / 2
    start = center - half_tickets + 0.5

    return max(1, int(start))


def parse_seat_position(position: str) -> Optional[Tuple[str, int]]:
    """
    Parse a seat position string like 'A1', 'H10', 'b5'.

    Args:
        position: Seat position string

    Returns:
        Tuple of (row_letter, column_number) or None if invalid
    """
    if not position:
        return None

    position = position.strip().upper()

    # Match pattern: one letter followed by one or more digits
    match = re.match(r'^([A-Z])(\d+)$', position)
    if not match:
        return None

    row_letter = match.group(1)
    col_number = int(match.group(2))

    return (row_letter, col_number)


def get_available_seats_in_row(
    db: Session,
    movie_id: int,
    row_letter: str
) -> List[Seat]:
    """
    Get all available (unbooked) seats in a specific row.

    Args:
        db: Database session
        movie_id: Movie ID
        row_letter: Row letter (A-Z)

    Returns:
        List of available Seat objects, ordered by seat number
    """
    return db.query(Seat).filter(
        Seat.movie_id == movie_id,
        Seat.row_letter == row_letter,
        Seat.is_booked == False
    ).order_by(Seat.seat_number).all()


def get_row_letters_for_movie(db: Session, movie_id: int) -> List[str]:
    """
    Get all row letters for a movie, ordered from furthest to closest to screen.

    In the display convention:
        SCREEN
    ----------------
    H . . . . . . . .   <- Front row (closest to screen)
    G . . . . . . . .
    ...
    A . . . . . . . .   <- Back row (furthest from screen)

    So we return ['A', 'B', 'C', ...] to start from the back row.

    Args:
        db: Database session
        movie_id: Movie ID

    Returns:
        List of row letters starting from back row (A first)
    """
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        return []

    # Return A, B, C, ... (A is back row, furthest from screen)
    row_letters = list(string.ascii_uppercase[:movie.rows])
    return row_letters  # A first (back row)


def get_default_seats(
    db: Session,
    movie_id: int,
    num_tickets: int
) -> List[Seat]:
    """
    Get seats using default selection algorithm:
    1. Start from furthest row from screen
    2. Start from middle-most column
    3. Overflow to next row closer to screen

    Args:
        db: Database session
        movie_id: Movie ID
        num_tickets: Number of tickets to allocate

    Returns:
        List of selected Seat objects
    """
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        return []

    selected_seats = []
    remaining = num_tickets
    row_letters = get_row_letters_for_movie(db, movie_id)

    for row_letter in row_letters:
        if remaining <= 0:
            break

        available = get_available_seats_in_row(db, movie_id, row_letter)
        if not available:
            continue

        # Calculate how many to take from this row
        to_take = min(remaining, len(available))

        # Calculate centered starting position
        start_col = get_middle_start_column(movie.seats_per_row, to_take)

        # Find consecutive available seats starting from middle
        # First, try to get seats centered around the middle
        selected_from_row = select_centered_seats(available, to_take, start_col)

        selected_seats.extend(selected_from_row)
        remaining -= len(selected_from_row)

    return selected_seats


def select_centered_seats(
    available_seats: List[Seat],
    count: int,
    preferred_start: int
) -> List[Seat]:
    """
    Select seats trying to center them around the preferred starting column.

    Args:
        available_seats: List of available seats in the row
        count: Number of seats to select
        preferred_start: Preferred starting column

    Returns:
        List of selected seats
    """
    if not available_seats or count <= 0:
        return []

    # Create a map of available seat numbers
    available_map = {s.seat_number: s for s in available_seats}
    available_numbers = sorted(available_map.keys())

    if count >= len(available_numbers):
        return available_seats[:count]

    # Try to find consecutive seats starting from preferred position
    best_start_idx = 0
    best_distance = float('inf')

    for i in range(len(available_numbers) - count + 1):
        # Check if these seats are consecutive
        consecutive = True
        for j in range(count - 1):
            if available_numbers[i + j + 1] - available_numbers[i + j] != 1:
                consecutive = False
                break

        if consecutive:
            # Calculate distance from preferred start
            actual_start = available_numbers[i]
            distance = abs(actual_start - preferred_start)
            if distance < best_distance:
                best_distance = distance
                best_start_idx = i

    # If no consecutive block found, just take the first available seats
    selected_numbers = available_numbers[best_start_idx:best_start_idx + count]
    return [available_map[n] for n in selected_numbers]


def get_seats_from_position(
    db: Session,
    movie_id: int,
    start_row: str,
    start_col: int,
    num_tickets: int
) -> List[Seat]:
    """
    Get seats starting from a specific position:
    1. Fill empty seats to the right in the same row
    2. Overflow to next row closer to screen using default rules

    In display convention, A is back row, H is front row.
    So overflow goes A -> B -> C -> ... -> H (toward screen)

    Args:
        db: Database session
        movie_id: Movie ID
        start_row: Starting row letter
        start_col: Starting column number
        num_tickets: Number of tickets to allocate

    Returns:
        List of selected Seat objects
    """
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        return []

    selected_seats = []
    remaining = num_tickets

    # Get all row letters
    all_rows = list(string.ascii_uppercase[:movie.rows])
    start_idx = all_rows.index(start_row) if start_row in all_rows else -1
    if start_idx == -1:
        return []

    # Rows from start_row toward screen (A -> B -> C -> ... -> H)
    rows_to_check = all_rows[start_idx:]

    is_first_row = True
    for row_letter in rows_to_check:
        if remaining <= 0:
            break

        available = get_available_seats_in_row(db, movie_id, row_letter)
        if not available:
            continue

        if is_first_row:
            # First row: fill from start_col to the right
            seats_to_right = [s for s in available if s.seat_number >= start_col]
            seats_to_right.sort(key=lambda s: s.seat_number)

            to_take = min(remaining, len(seats_to_right))
            selected_seats.extend(seats_to_right[:to_take])
            remaining -= to_take
            is_first_row = False
        else:
            # Subsequent rows: use default centered selection
            to_take = min(remaining, len(available))
            start_col_centered = get_middle_start_column(movie.seats_per_row, to_take)
            selected_from_row = select_centered_seats(available, to_take, start_col_centered)
            selected_seats.extend(selected_from_row)
            remaining -= len(selected_from_row)

    return selected_seats


def allocate_seats(
    db: Session,
    movie_id: int,
    num_tickets: int,
    start_position: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main allocation function that handles both default and custom position allocation.

    Args:
        db: Database session
        movie_id: Movie ID
        num_tickets: Number of tickets to allocate
        start_position: Optional starting position (e.g., 'A1', 'H5')

    Returns:
        Dictionary with:
        - success: bool
        - seats: List of allocated seats (if successful)
        - error: Error message (if not successful)
    """
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        return {'success': False, 'error': 'Movie not found', 'seats': []}

    # Check total available seats
    total_available = db.query(Seat).filter(
        Seat.movie_id == movie_id,
        Seat.is_booked == False
    ).count()

    if total_available < num_tickets:
        return {
            'success': False,
            'error': f'Not enough seats available. Only {total_available} seats remaining.',
            'seats': []
        }

    # Allocate seats
    if start_position:
        parsed = parse_seat_position(start_position)
        if not parsed:
            return {
                'success': False,
                'error': f'Invalid seat position: {start_position}',
                'seats': []
            }

        row_letter, col_number = parsed

        # Validate row exists
        row_letters = list(string.ascii_uppercase[:movie.rows])
        if row_letter not in row_letters:
            return {
                'success': False,
                'error': f'Invalid row: {row_letter}. Valid rows are A-{row_letters[-1]}',
                'seats': []
            }

        # Validate column exists
        if col_number < 1 or col_number > movie.seats_per_row:
            return {
                'success': False,
                'error': f'Invalid column: {col_number}. Valid columns are 1-{movie.seats_per_row}',
                'seats': []
            }

        seats = get_seats_from_position(db, movie_id, row_letter, col_number, num_tickets)
    else:
        seats = get_default_seats(db, movie_id, num_tickets)

    if len(seats) < num_tickets:
        return {
            'success': False,
            'error': f'Could not allocate {num_tickets} contiguous seats. Try a different position.',
            'seats': []
        }

    return {'success': True, 'seats': seats, 'error': None}


def get_seating_map(
    db: Session,
    movie_id: int,
    selected_seat_ids: Optional[List[int]] = None
) -> Dict[str, List[Dict]]:
    """
    Get the complete seating map for display.

    Args:
        db: Database session
        movie_id: Movie ID
        selected_seat_ids: IDs of seats selected for current booking

    Returns:
        Dictionary mapping row letters to list of seat info dicts
    """
    selected_ids = set(selected_seat_ids or [])

    seats = db.query(Seat).filter(Seat.movie_id == movie_id).order_by(
        Seat.row_letter, Seat.seat_number
    ).all()

    seating_map = {}
    for seat in seats:
        if seat.row_letter not in seating_map:
            seating_map[seat.row_letter] = []

        status = 'available'
        if seat.id in selected_ids:
            status = 'selected'
        elif seat.is_booked:
            status = 'booked'

        seating_map[seat.row_letter].append({
            'id': seat.id,
            'number': seat.seat_number,
            'label': seat.seat_label,
            'status': status
        })

    return seating_map
