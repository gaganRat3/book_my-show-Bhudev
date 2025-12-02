from django.core.management.base import BaseCommand
from core.models import Seat

class Command(BaseCommand):
    help = 'Populate seats for the venue'

    def handle(self, *args, **options):
        # Example seat layout: rows and seat numbers
        seat_layout = {
            'A': 36, 'B': 37, 'C': 37, 'D': 38, 'E': 39, 'F': 40, 'G': 41, 'H': 34, 'I': 34,
            'J': 36, 'K': 36, 'L': 38, 'M': 37, 'N': 38, 'O': 38, 'P': 46, 'Q': 44, 'R': 43,
            'S': 41, 'T': 40, 'U': 37, 'V': 34, 'W': 34, 'X': 33, 'Y': 28, 'Z': 26,
            'AA': 35, 'BB': 35
        }
        count = 0
        for row, max_seat in seat_layout.items():
            for num in range(1, max_seat + 1):
                seat_number = f"{row}-{num}"
                _, created = Seat.objects.get_or_create(seat_number=seat_number)
                if created:
                    count += 1
        self.stdout.write(self.style.SUCCESS(f'{count} seats populated.'))
