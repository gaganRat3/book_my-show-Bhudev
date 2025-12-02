from events.models import Event, Seat

# Example seat layout: rows and seat numbers
seat_layout = {
    'top-left1': {'rows': ['P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X'], 'seats_per_row': [11, 10, 8, 8, 7, 6, 5, 3, 2]},
    'top-left2': {'rows': ['P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y'], 'seats_per_row': [18, 20, 20, 20, 19, 18, 17, 16, 14, 14]},
    'top-right2': {'rows': ['P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y'], 'seats_per_row': [35, 33, 33, 33, 32, 31, 30, 29, 27, 27]},
    # Add other sections as needed
}

def populate_seats_for_all_events():
    for event in Event.objects.all():
        for section, layout in seat_layout.items():
            for row, seats_in_row in zip(layout['rows'], layout['seats_per_row']):
                for seat_num in range(1, seats_in_row + 1):
                    seat_number = f"{row}{seat_num}"
                    Seat.objects.get_or_create(event=event, seat_number=seat_number)

if __name__ == "__main__":
    populate_seats_for_all_events()
    print("Seats populated for all events.")
