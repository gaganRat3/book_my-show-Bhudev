from core.models import Seat

# Example mapping function: customize this to match your template's data-id format
# For instance, if your template uses 'O1-1', 'O1-2', etc., and your DB has 'O1_1', 'O1_2', etc.
# You may need to adjust this logic to fit your actual template


# Convert 'R6' to 'R-6' format
import re
def map_seat_number_to_template(seat_number):
    match = re.match(r'^([A-Z]+)(\d+)$', seat_number)
    if match:
        row = match.group(1)
        num = match.group(2)
        return f"{row}-{num}"
    return seat_number  # fallback if already correct or doesn't match


def update_seat_numbers():
    for seat in Seat.objects.all():
        new_seat_number = map_seat_number_to_template(seat.seat_number)
        if seat.seat_number != new_seat_number:
            print(f"Updating seat {seat.id}: {seat.seat_number} -> {new_seat_number}")
            seat.seat_number = new_seat_number
            seat.save()
    print("Seat numbers updated to match template format.")

if __name__ == "__main__":
    update_seat_numbers()
