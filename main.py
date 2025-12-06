from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
import string
from typing import Optional, List

from database import engine, get_db, Base
from models import Movie, Seat, Booking, BookingSeat
from seat_allocation import (
    allocate_seats,
    get_seating_map,
    parse_seat_position
)

app = FastAPI(title="GIC Cinemas Booking System")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Mapping of TDD days to templates
TDD_TEMPLATES = {
    "one": "tdd-portfolio.html",
    "two": "tdd-refactoring-portfolio.html",
    "three": "tdd-loyalty-portfolio.html",
    "four": "tdd-solid-portfolio.html",
    "five": "tdd-state-machine-portfolio.html",
    "six": "tdd-solid-pricing-portfolio.html",
}

@app.get("/tdd_day_{day}", response_class=HTMLResponse)
async def tdd_landing(request: Request, day: str):
    """Landing page for a specific day of TDD journey"""
    template_name = TDD_TEMPLATES.get(day.lower())
    if not template_name:
        raise HTTPException(status_code=404, detail="Day not found")
    return templates.TemplateResponse(template_name, {"request": request})


@app.on_event("startup")
def startup_event():
    """Create database tables on startup"""
    Base.metadata.create_all(bind=engine)


def generate_booking_id(db: Session) -> str:
    """Generate unique booking ID like GIC0001, GIC0002, etc."""
    last_booking = db.query(Booking).order_by(Booking.id.desc()).first()
    if last_booking:
        # Extract number from last booking ID
        last_num = int(last_booking.booking_id.replace("GIC", ""))
        new_num = last_num + 1
    else:
        new_num = 1
    return f"GIC{new_num:04d}"


def create_seats_for_movie(db: Session, movie: Movie):
    """Create all seats for a movie based on rows and seats_per_row"""
    row_letters = string.ascii_uppercase[:movie.rows]

    for row_letter in row_letters:
        for seat_num in range(1, movie.seats_per_row + 1):
            seat = Seat(
                movie_id=movie.id,
                row_letter=row_letter,
                seat_number=seat_num,
                is_booked=False
            )
            db.add(seat)
    db.commit()


def get_active_movie(db: Session) -> Optional[Movie]:
    """Get the currently active movie"""
    return db.query(Movie).filter(Movie.is_active == True).first()


# ============== ROUTES ==============

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    """Home page - setup or main menu"""
    movie = get_active_movie(db)

    if movie:
        # Show main menu
        available_seats = db.query(Seat).filter(
            Seat.movie_id == movie.id,
            Seat.is_booked == False
        ).count()

        return templates.TemplateResponse("main_menu.html", {
            "request": request,
            "movie": movie,
            "available_seats": available_seats
        })
    else:
        # Show setup page
        return templates.TemplateResponse("setup.html", {
            "request": request,
            "error": None
        })

@app.get("/setup", response_class=HTMLResponse)
async def setup_form(request: Request):
    return templates.TemplateResponse("setup.html", {"request": request})


@app.post("/setup", response_class=HTMLResponse)
async def setup_movie(
    request: Request,
    title: str = Form(...),
    rows: int = Form(...),
    seats_per_row: int = Form(...),
    db: Session = Depends(get_db)
):
    """Setup a new movie with seating configuration"""
    # Validation
    errors = []

    if not title or not title.strip():
        errors.append("Movie title is required")

    if rows < 1 or rows > 26:
        errors.append("Number of rows must be between 1 and 26")

    if seats_per_row < 1 or seats_per_row > 50:
        errors.append("Seats per row must be between 1 and 50")

    if errors:
        return templates.TemplateResponse("setup.html", {
            "request": request,
            "error": " | ".join(errors),
            "title": title,
            "rows": rows,
            "seats_per_row": seats_per_row
        })

    # Deactivate any existing active movie
    db.query(Movie).filter(Movie.is_active == True).update({"is_active": False})

    # Create new movie
    movie = Movie(
        title=title.strip(),
        rows=rows,
        seats_per_row=seats_per_row,
        is_active=True
    )
    db.add(movie)
    db.commit()
    db.refresh(movie)

    # Create seats
    create_seats_for_movie(db, movie)

    return RedirectResponse(url="/", status_code=303)


@app.get("/book", response_class=HTMLResponse)
async def book_tickets_page(request: Request, db: Session = Depends(get_db)):
    """Show ticket quantity input page"""
    movie = get_active_movie(db)

    if not movie:
        return RedirectResponse(url="/", status_code=303)

    available_seats = db.query(Seat).filter(
        Seat.movie_id == movie.id,
        Seat.is_booked == False
    ).count()

    error = request.query_params.get('error')

    return templates.TemplateResponse("book_step1.html", {
        "request": request,
        "movie": movie,
        "available_seats": available_seats,
        "error": error
    })


@app.post("/book/allocate", response_class=HTMLResponse)
async def allocate_tickets(
    request: Request,
    num_tickets: int = Form(...),
    db: Session = Depends(get_db)
):
    """Allocate seats and show seating map with default selection"""
    movie = get_active_movie(db)

    if not movie:
        return RedirectResponse(url="/", status_code=303)

    # Validate number of tickets
    if num_tickets < 1:
        return RedirectResponse(url="/book?error=invalid_count", status_code=303)

    # Check available seats
    available_count = db.query(Seat).filter(
        Seat.movie_id == movie.id,
        Seat.is_booked == False
    ).count()

    if num_tickets > available_count:
        return RedirectResponse(
            url=f"/book?error=not_enough&requested={num_tickets}&available={available_count}",
            status_code=303
        )

    # Allocate seats using default algorithm
    result = allocate_seats(db, movie.id, num_tickets)

    if not result['success']:
        return RedirectResponse(url=f"/book?error=allocation_failed", status_code=303)

    # Get seat IDs for the selected seats
    selected_seat_ids = [s.id for s in result['seats']]

    # Safeguard: ensure we actually got seats
    if not selected_seat_ids:
        return RedirectResponse(url=f"/book?error=no_seats_allocated", status_code=303)

    # Get seating map
    seating_map = get_seating_map(db, movie.id, selected_seat_ids)

    # Generate a temporary booking ID for display
    temp_booking_id = generate_booking_id(db)

    return templates.TemplateResponse("book_step2.html", {
        "request": request,
        "movie": movie,
        "num_tickets": num_tickets,
        "selected_seats": result['seats'],
        "selected_seat_ids": selected_seat_ids,
        "seat_ids": ",".join(str(sid) for sid in selected_seat_ids),
        "seating_map": seating_map,
        "booking_id": temp_booking_id,
        "available_count": available_count - num_tickets,
        "error": None
    })


@app.post("/book/change-position", response_class=HTMLResponse)
async def change_seat_position(
    request: Request,
    num_tickets: int = Form(...),
    start_position: str = Form(...),
    db: Session = Depends(get_db)
):
    """Change seat selection starting from specified position"""
    movie = get_active_movie(db)

    if not movie:
        return RedirectResponse(url="/", status_code=303)

    # Allocate seats from custom position
    result = allocate_seats(db, movie.id, num_tickets, start_position=start_position)

    if not result['success']:
        # Re-allocate with default and show error
        default_result = allocate_seats(db, movie.id, num_tickets)
        selected_seat_ids = [s.id for s in default_result['seats']] if default_result['success'] else []
        seating_map = get_seating_map(db, movie.id, selected_seat_ids)

        available_count = db.query(Seat).filter(
            Seat.movie_id == movie.id,
            Seat.is_booked == False
        ).count()

        return templates.TemplateResponse("book_step2.html", {
            "request": request,
            "movie": movie,
            "num_tickets": num_tickets,
            "selected_seats": default_result.get('seats', []),
            "selected_seat_ids": selected_seat_ids,
            "seat_ids": ",".join(str(sid) for sid in selected_seat_ids),
            "seating_map": seating_map,
            "booking_id": generate_booking_id(db),
            "available_count": available_count - num_tickets,
            "error": result['error']
        })

    selected_seat_ids = [s.id for s in result['seats']]
    seating_map = get_seating_map(db, movie.id, selected_seat_ids)

    available_count = db.query(Seat).filter(
        Seat.movie_id == movie.id,
        Seat.is_booked == False
    ).count()

    return templates.TemplateResponse("book_step2.html", {
        "request": request,
        "movie": movie,
        "num_tickets": num_tickets,
        "selected_seats": result['seats'],
        "selected_seat_ids": selected_seat_ids,
        "seat_ids": ",".join(str(sid) for sid in selected_seat_ids),
        "seating_map": seating_map,
        "booking_id": generate_booking_id(db),
        "available_count": available_count - num_tickets,
        "error": None
    })


@app.post("/book/confirm", response_class=HTMLResponse)
async def confirm_booking(
    request: Request,
    seat_ids: str = Form(default=""),  # Allow empty, handle gracefully
    db: Session = Depends(get_db)
):
    """Confirm and finalize the booking"""
    movie = get_active_movie(db)

    if not movie:
        return RedirectResponse(url="/", status_code=303)

    # Handle empty or invalid seat_ids
    if not seat_ids or not seat_ids.strip():
        return RedirectResponse(url="/book?error=no_seats_selected", status_code=303)

    # Parse seat IDs
    try:
        seat_id_list = [int(x) for x in seat_ids.split(',') if x.strip()]
    except ValueError:
        return RedirectResponse(url="/book?error=invalid_seats", status_code=303)

    if not seat_id_list:
        return RedirectResponse(url="/book?error=no_seats", status_code=303)

    # Verify all seats are still available
    seats = db.query(Seat).filter(
        Seat.id.in_(seat_id_list),
        Seat.movie_id == movie.id,
        Seat.is_booked == False
    ).all()

    if len(seats) != len(seat_id_list):
        return RedirectResponse(url="/book?error=seats_taken", status_code=303)

    # Create booking
    booking_id = generate_booking_id(db)
    booking = Booking(
        movie_id=movie.id,
        booking_id=booking_id
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    # Mark seats as booked and link to booking
    for seat in seats:
        seat.is_booked = True
        booking_seat = BookingSeat(
            booking_id=booking.id,
            seat_id=seat.id
        )
        db.add(booking_seat)

    db.commit()

    return RedirectResponse(url=f"/booking/{booking_id}", status_code=303)


@app.post("/book", response_class=HTMLResponse)
async def book_tickets(
    request: Request,
    seat_ids: list = Form(default=[]),
    db: Session = Depends(get_db)
):
    """Process ticket booking (legacy endpoint for compatibility)"""
    movie = get_active_movie(db)

    if not movie:
        return RedirectResponse(url="/", status_code=303)

    # Handle form data - seats might come as comma-separated string
    form_data = await request.form()
    seat_ids_raw = form_data.getlist("seat_ids")

    # Flatten and convert to integers
    seat_ids = []
    for item in seat_ids_raw:
        if isinstance(item, str) and ',' in item:
            seat_ids.extend([int(x) for x in item.split(',') if x])
        elif item:
            seat_ids.append(int(item))

    if not seat_ids:
        # No seats selected, redirect back
        return RedirectResponse(url="/book?error=no_seats", status_code=303)

    # Verify seats are available
    seats = db.query(Seat).filter(
        Seat.id.in_(seat_ids),
        Seat.movie_id == movie.id,
        Seat.is_booked == False
    ).all()

    if len(seats) != len(seat_ids):
        return RedirectResponse(url="/book?error=seats_taken", status_code=303)

    # Create booking
    booking_id = generate_booking_id(db)
    booking = Booking(
        movie_id=movie.id,
        booking_id=booking_id
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    # Mark seats as booked and link to booking
    for seat in seats:
        seat.is_booked = True
        booking_seat = BookingSeat(
            booking_id=booking.id,
            seat_id=seat.id
        )
        db.add(booking_seat)

    db.commit()

    return RedirectResponse(url=f"/booking/{booking_id}", status_code=303)


@app.get("/booking/{booking_id}", response_class=HTMLResponse)
async def view_booking(
    request: Request,
    booking_id: str,
    db: Session = Depends(get_db),
    show_map: bool = False
):
    """View a specific booking confirmation"""
    booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Get booked seats for this booking
    seats = [bs.seat for bs in booking.booking_seats]
    seats_sorted = sorted(seats, key=lambda s: (s.row_letter, s.seat_number))

    # If show_map is requested, generate seating map with markers
    seating_map = None
    if show_map:
        seating_map = get_booking_seating_map(db, booking)

    return templates.TemplateResponse("booking_confirmation.html", {
        "request": request,
        "booking": booking,
        "seats": seats_sorted,
        "movie": booking.movie,
        "seating_map": seating_map,
        "show_map": show_map
    })


def get_booking_seating_map(db: Session, viewing_booking: Booking) -> dict:
    """
    Generate seating map for viewing a specific booking.

    Returns dict with:
    - rows: list of row data with seats marked as:
      - 'o' for seats in the viewed booking
      - '#' for seats in other bookings
      - '.' for available seats
    - movie: the movie info
    """
    movie = viewing_booking.movie

    # Get all seats for the movie
    all_seats = db.query(Seat).filter(Seat.movie_id == movie.id).all()

    # Get seat IDs for the viewed booking
    viewed_booking_seat_ids = {bs.seat_id for bs in viewing_booking.booking_seats}

    # Get all booked seat IDs (from all bookings)
    all_booked_seats = db.query(BookingSeat).join(Seat).filter(
        Seat.movie_id == movie.id
    ).all()
    other_booked_seat_ids = {bs.seat_id for bs in all_booked_seats if bs.seat_id not in viewed_booking_seat_ids}

    # Build the seating map
    row_letters = sorted(set(s.row_letter for s in all_seats), reverse=True)  # H to A (screen at top)
    seats_per_row = movie.seats_per_row

    rows = []
    for row_letter in row_letters:
        row_seats = []
        for seat_num in range(1, seats_per_row + 1):
            seat = next((s for s in all_seats if s.row_letter == row_letter and s.seat_number == seat_num), None)
            if seat:
                if seat.id in viewed_booking_seat_ids:
                    marker = 'o'  # This booking's seats
                elif seat.id in other_booked_seat_ids:
                    marker = '#'  # Other bookings' seats
                else:
                    marker = '.'  # Available
            else:
                marker = '.'
            row_seats.append({
                'number': seat_num,
                'marker': marker,
                'label': f"{row_letter}{seat_num}"
            })
        rows.append({
            'letter': row_letter,
            'seats': row_seats
        })

    return {
        'rows': rows,
        'seats_per_row': seats_per_row,
        'movie': movie
    }


@app.get("/bookings", response_class=HTMLResponse)
async def check_bookings(request: Request, db: Session = Depends(get_db)):
    """View all bookings"""
    movie = get_active_movie(db)

    if not movie:
        return RedirectResponse(url="/", status_code=303)

    bookings = db.query(Booking).filter(
        Booking.movie_id == movie.id
    ).order_by(Booking.created_at.desc()).all()

    return templates.TemplateResponse("bookings.html", {
        "request": request,
        "movie": movie,
        "bookings": bookings
    })


@app.post("/bookings/search")
async def search_booking(booking_id: str = Form(""), db: Session = Depends(get_db)):
    """Search for a specific booking by ID"""
    if not booking_id.strip():
        # Blank input - go back to main menu
        return RedirectResponse(url="/", status_code=303)

    # Redirect to booking view with show_map=true
    return RedirectResponse(url=f"/booking/{booking_id.strip()}?show_map=true", status_code=303)


@app.get("/reset", response_class=HTMLResponse)
async def reset_system(request: Request, db: Session = Depends(get_db)):
    """Reset the system - go back to setup"""
    # Deactivate all movies
    db.query(Movie).update({"is_active": False})
    db.commit()

    return RedirectResponse(url="/", status_code=303)


@app.get("/exit", response_class=HTMLResponse)
async def exit_system(request: Request):
    """Exit the system with a thank you message"""
    return templates.TemplateResponse("exit.html", {
        "request": request
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
