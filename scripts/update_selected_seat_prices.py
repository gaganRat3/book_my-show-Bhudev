
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyshow.settings')
django.setup()

from core.models import SelectedSeat, Seat

def update_selected_seat_prices():
    count = 0
    for selected in SelectedSeat.objects.all():
        if selected.seat and selected.seat.price is not None:
            selected.price = selected.seat.price
            selected.save()
            count += 1
    print(f"Updated price for {count} SelectedSeat records.")

if __name__ == "__main__":
    update_selected_seat_prices()
