from django.core.management.base import BaseCommand
from core.seat_reservation_service import SeatReservationService


class Command(BaseCommand):
    help = 'Release expired seat holds'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Display detailed output',
        )

    def handle(self, *args, **options):
        verbose = options['verbose']
        
        if verbose:
            self.stdout.write('Starting cleanup of expired seat holds...')
        
        released_count = SeatReservationService.cleanup_expired_holds()
        
        if verbose or released_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully released {released_count} expired seat holds'
                )
            )
        elif verbose:
            self.stdout.write('No expired holds found')