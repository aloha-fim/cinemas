# GIC Cinemas - Cinema Booking Management System

A FastAPI-based cinema booking management system with PostgreSQL database and Jinja2 templates.

## Features

- **Movie Setup**: Define movie title and seating configuration (rows × seats per row)
- **Smart Seat Allocation**: Automatic seat selection from back row, centered
- **Custom Position Selection**: Choose your own starting seat position
- **Overflow Handling**: Seats overflow to next row closer to screen
- **Booking Management**: Create and track bookings with unique IDs (GIC0001, GIC0002, etc.)
- **Responsive Design**: Works on desktop and mobile devices
- **Comprehensive Tests**: TDD approach with 50+ unit and integration tests

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: Jinja2 Templates + Bootstrap 5
- **Testing**: pytest with SQLite in-memory database
- **Styling**: Custom CSS with modern design

## Project Structure

```
cinema_booking/
├── main.py              # FastAPI application and routes
├── database.py          # Database configuration
├── models.py            # SQLAlchemy models
├── seat_allocation.py   # Seat selection algorithms
├── requirements.txt     # Python dependencies
├── pytest.ini           # Pytest configuration
├── .env                 # Environment variables
├── .env.example         # Example environment file
├── templates/
│   ├── base.html        # Base template
│   ├── setup.html       # Movie setup page
│   ├── main_menu.html   # Main menu
│   ├── book_step1.html  # Ticket count input
│   ├── book_step2.html  # Seat selection with map
│   ├── booking_confirmation.html
│   └── bookings.html    # All bookings list
├── static/
│   └── css/
│       └── style.css    # Custom styles
└── tests/
    ├── __init__.py
    ├── test_seat_allocation.py  # Seat algorithm tests
    └── test_api.py              # API route tests
```

## Setup Instructions

### 1. Prerequisites

- Python 3.9+
- PostgreSQL 12+

### 2. Create PostgreSQL Database

```sql
CREATE DATABASE cinema_booking;
```

### 3. Configure Environment

Create `.env` and update with your database credentials:

```bash
echo. > .env (Windows)
touch .env (Mac)
```

Edit `.env`:
```
DATABASE_URL=postgresql://username:password@localhost:5432/cinema_booking
```

### 4. Install Dependencies

```bash
python -m venv venv (windows virtual env)
venv/Scripts/activate (windows command)

pip install -r requirements.txt
```

### 5. Run the Application

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or simply:
```bash
python main.py
```

### 6. Access the Application

Open your browser and navigate to: `http://localhost:8000`

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_seat_allocation.py

# Run with coverage
pytest --cov=. --cov-report=html
```

## Usage

### Application Start

1. Enter movie title, number of rows (1-26), and seats per row (1-50)
2. Example: "Inception" with 8 rows and 10 seats creates an 80-seat cinema

### Main Menu

- **[1] Book tickets**: Start the booking workflow
- **[2] Check bookings**: View all existing bookings
- **[3] Exit**: Reset the system and configure a new movie

### Booking Workflow

1. **Enter ticket count**: Specify how many tickets you want
2. **View seat allocation**: System automatically selects seats from:
   - Furthest row from screen (back row)
   - Middle-most columns (centered)
3. **Change position (optional)**: Enter a different starting seat (e.g., "A1", "C5")
   - Seats fill to the right in the same row
   - Overflow to next row closer to screen
4. **Confirm booking**: Finalize and receive booking ID

### Seat Selection Algorithm

**Default Selection:**
- Starts from the furthest row from screen (e.g., row H in 8-row cinema)
- Seats are centered in the row
- If row can't fit all tickets, overflow to next row closer to screen

**Custom Position Selection:**
- Starts from specified seat (e.g., B3)
- Fills available seats to the right
- Overflows to next row with default centering rules

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page (setup or main menu) |
| POST | `/setup` | Create new movie configuration |
| GET | `/book` | Enter ticket count (step 1) |
| POST | `/book/allocate` | Allocate seats and show map (step 2) |
| POST | `/book/change-position` | Change starting seat position |
| POST | `/book/confirm` | Confirm and finalize booking |
| GET | `/booking/{id}` | View specific booking |
| GET | `/bookings` | List all bookings |
| GET | `/reset` | Reset system |

## Constraints

- Maximum rows: 26 (A-Z)
- Maximum seats per row: 50
- Seat labels: Row letter + seat number (e.g., A1, B10, H5)

## License

MIT License
