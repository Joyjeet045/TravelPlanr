from langchain_core.tools import tool
from travel_assistant.database.db_utils import db
import sqlite3
from datetime import date, datetime
from typing import Optional, Union

@tool
def search_car_rentals(
    location: Optional[str] = None,
    name: Optional[str] = None,
    price_tier: Optional[str] = None,
    start_date: Optional[Union[datetime, date]] = None,
    end_date: Optional[Union[datetime, date]] = None,
) -> list[dict]:
    """Search for car rentals based on location, name, price tier, start date, and end date.
    Args:
        location (str, optional): Location of the car rental.
        name (str, optional): Name of the car rental company.
        price_tier (str, optional): Price tier of the car rental.
        start_date (datetime/date, optional): Start date of the car rental.
        end_date (datetime/date, optional): End date of the car rental.
    Returns:
        List of car rental dictionaries matching the search criteria.
    """
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    query = "SELECT * FROM car_rentals WHERE 1=1"
    params = []
    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")
    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return [
        dict(zip([column[0] for column in cursor.description], row)) for row in results
    ]

@tool
def book_car_rental(rental_id: int) -> str:
    """Book a car rental by its ID.
    Args:
        rental_id (int): The ID of the car rental to book.
    Returns:
        Success or error message.
    """
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("UPDATE car_rentals SET booked = 1 WHERE id = ?", (rental_id,))
    conn.commit()
    if cursor.rowcount > 0:
        conn.close()
        return f"Car rental {rental_id} successfully booked."
    else:
        conn.close()
        return f"No car rental found with ID {rental_id}."

@tool
def update_car_rental(
    rental_id: int,
    start_date: Optional[Union[datetime, date]] = None,
    end_date: Optional[Union[datetime, date]] = None,
) -> str:
    """Update a car rental's start and end dates by its ID.
    Args:
        rental_id (int): The ID of the car rental to update.
        start_date (datetime/date, optional): The new start date.
        end_date (datetime/date, optional): The new end date.
    Returns:
        Success or error message.
    """
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    if start_date:
        cursor.execute(
            "UPDATE car_rentals SET start_date = ? WHERE id = ?",
            (start_date, rental_id),
        )
    if end_date:
        cursor.execute(
            "UPDATE car_rentals SET end_date = ? WHERE id = ?", (end_date, rental_id)
        )
    conn.commit()
    if cursor.rowcount > 0:
        conn.close()
        return f"Car rental {rental_id} successfully updated."
    else:
        conn.close()
        return f"No car rental found with ID {rental_id}."

@tool
def cancel_car_rental(rental_id: int) -> str:
    """Cancel a car rental by its ID.
    Args:
        rental_id (int): The ID of the car rental to cancel.
    Returns:
        Success or error message.
    """
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("UPDATE car_rentals SET booked = 0 WHERE id = ?", (rental_id,))
    conn.commit()
    if cursor.rowcount > 0:
        conn.close()
        return f"Car rental {rental_id} successfully cancelled."
    else:
        conn.close()
        return f"No car rental found with ID {rental_id}." 