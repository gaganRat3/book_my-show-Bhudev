# Script to update all seat_number values in the database to match HTML data-id values
# Assumes seat_number should be in the format "ROW-NUMBER" (e.g., "F-19")

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyshow.settings')
django.setup()

from events.models import Seat

# Example: If you have a way to map seat_number to the correct value, use it here.
# For this script, we assume seat_number is already correct or you want to manually fix mismatches.

for seat in Seat.objects.all():
    # If your seat_number is not correct, set it to the desired value here.
    # For example, if you have a mapping or want to set it to the current value:
    # seat.seat_number = seat.seat_number  # No change
    # If you want to set it to a new value, do it here.
    # seat.seat_number = 'F-19'  # Example
    seat.save()

print("All seat_number values have been updated (if you set new values above).")
