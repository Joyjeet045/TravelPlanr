from langchain_core.tools import tool
from travel_assistant.database.db_utils import db
import sqlite3
from datetime import date, datetime
from typing import Optional, Union

@tool
def search_hotels(
    location: Optional[str] = None,
    name: Optional[str] = None,
    price_tier: Optional[str] = None,
    checkin_date: Optional[Union[datetime, date]] = None,
    checkout_date: Optional[Union[datetime, date]] = None,
) -> list[dict]:
    """Search for hotels based on location, name, price tier, check-in date, and check-out date.
    Args:
        location (str, optional): Location of the hotel.
        name (str, optional): Name of the hotel.
        price_tier (str, optional): Price tier of the hotel.
        checkin_date (datetime/date, optional): Check-in date.
        checkout_date (datetime/date, optional): Check-out date.
    Returns:
        List of hotel dictionaries matching the search criteria.
    """
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    query = "SELECT * FROM hotels WHERE 1=1"
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
def book_hotel(hotel_id: int) -> str:
    """Book a hotel by its ID.
    Args:
        hotel_id (int): The ID of the hotel to book.
    Returns:
        Success or error message.
    """
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("UPDATE hotels SET booked = 1 WHERE id = ?", (hotel_id,))
    conn.commit()
    if cursor.rowcount > 0:
        conn.close()
        return f"Hotel {hotel_id} successfully booked."
    else:
        conn.close()
        return f"No hotel found with ID {hotel_id}."

@tool
def update_hotel(
    hotel_id: int,
    checkin_date: Optional[Union[datetime, date]] = None,
    checkout_date: Optional[Union[datetime, date]] = None,
) -> str:
    """Update a hotel's check-in and check-out dates by its ID.
    Args:
        hotel_id (int): The ID of the hotel to update.
        checkin_date (datetime/date, optional): The new check-in date.
        checkout_date (datetime/date, optional): The new check-out date.
    Returns:
        Success or error message.
    """
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    if checkin_date:
        cursor.execute(
            "UPDATE hotels SET checkin_date = ? WHERE id = ?", (checkin_date, hotel_id)
        )
    if checkout_date:
        cursor.execute(
            "UPDATE hotels SET checkout_date = ? WHERE id = ?",
            (checkout_date, hotel_id),
        )
    conn.commit()
    if cursor.rowcount > 0:
        conn.close()
        return f"Hotel {hotel_id} successfully updated."
    else:
        conn.close()
        return f"No hotel found with ID {hotel_id}."

@tool
def cancel_hotel(hotel_id: int) -> str:
    """Cancel a hotel by its ID.
    Args:
        hotel_id (int): The ID of the hotel to cancel.
    Returns:
        Success or error message.
    """
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("UPDATE hotels SET booked = 0 WHERE id = ?", (hotel_id,))
    conn.commit()
    if cursor.rowcount > 0:
        conn.close()
        return f"Hotel {hotel_id} successfully cancelled."
    else:
        conn.close()
        return f"No hotel found with ID {hotel_id}." 