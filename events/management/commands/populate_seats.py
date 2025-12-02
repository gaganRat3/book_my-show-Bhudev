
from django.core.management.base import BaseCommand
from events.models import Event, Seat


# Generate seat list from provided ranges
seat_ranges = {
    "Z": 28, "Y": 28, "X": 33, "W": 34, "V": 34, "U": 37, "T": 40, "S": 41, "R": 43, "Q": 44, "P": 46,
    "O": 38, "N": 38, "M": 37, "L": 38, "K": 36, "J": 36, "I": 34, "H": 34, "G": 41, "F": 40, "E": 39,
    "D": 38, "C": 37, "B": 37, "A": 36, "BB": 35, "AA": 35
}
exact_seats = []
for row, max_seat in seat_ranges.items():
    for num in range(1, max_seat + 1):
        exact_seats.append((row, num))


