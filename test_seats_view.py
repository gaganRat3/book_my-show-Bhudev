#!/usr/bin/env python
import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyshow.settings')
django.setup()

from core.models import Seat, LandingFormData
from django.utils import timezone

def test_seat_view_data():
    """Test what data would be sent to the template"""
    print('TESTING SEAT VIEW DATA GENERATION:')
    print('=' * 50)
    
    # Simulate the view logic exactly
    current_time = timezone.now()
    
    # Get seats with different statuses  
    booked_seats = []
    held_seats = []
    user_held_seats = []
    
    # Refresh seats data after cleanup with explicit query
    seats = Seat.objects.all().order_by('seat_number')
    
    print(f"Total seats queried: {len(seats)}")
    
    # First, get ALL truly booked seats (regardless of user)
    definitely_booked = Seat.objects.filter(status='booked', is_booked=True)
    print(f"Found {len(definitely_booked)} definitely booked seats in database")
    
    for seat in definitely_booked:
        booked_seats.append(seat.seat_number)
        user_name = seat.reserved_by.name if seat.reserved_by else 'Unknown'
        print(f"Added booked seat: {seat.seat_number} (booked by {user_name})")
    
    # Simulate JSON encoding like the view does
    booked_seats_json = json.dumps(booked_seats)
    held_seats_json = json.dumps(held_seats)
    user_held_seats_json = json.dumps(user_held_seats)
    
    print(f"\nFINAL DATA THAT WOULD BE SENT TO FRONTEND:")
    print(f"  booked_seats JSON: {booked_seats_json}")
    print(f"  held_seats JSON: {held_seats_json}")
    print(f"  user_held_seats JSON: {user_held_seats_json}")
    
    print(f"\nThis data should appear in the browser console as:")
    print(f"  Booked seats from backend: {booked_seats_json}")

if __name__ == '__main__':
    test_seat_view_data()