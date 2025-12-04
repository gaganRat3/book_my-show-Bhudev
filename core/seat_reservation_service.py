from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import Seat, SelectedSeat, LandingFormData
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.exceptions import ValidationError


class SeatReservationService:
    """Service class for managing seat reservations, holds, and bookings"""
    
    HOLD_DURATION_MINUTES = 3
    
    @classmethod
    @transaction.atomic
    def hold_seats(cls, seat_numbers, user):
        """
        Hold multiple seats for a user atomically
        Returns: (success: bool, message: str, held_seats: list)
        """
        held_seats = []
        failed_seats = []
        
        # Use select_for_update to prevent race conditions
        seats = Seat.objects.select_for_update().filter(seat_number__in=seat_numbers)
        
        # Check all seats are available first
        for seat in seats:
            if not seat.is_available():
                if seat.reserved_by == user and seat.status == 'held':
                    # User already has this seat held, extend the hold
                    seat.reserved_until = timezone.now() + timedelta(minutes=cls.HOLD_DURATION_MINUTES)
                    seat.save()
                    held_seats.append(seat)
                else:
                    failed_seats.append(seat.seat_number)
        
        if failed_seats:
            return False, f"Seats {', '.join(failed_seats)} are not available", []
        
        # Hold all available seats
        for seat in seats:
            if seat not in held_seats:  # Don't re-hold already held seats
                if seat.hold_for_user(user, cls.HOLD_DURATION_MINUTES):
                    held_seats.append(seat)
        
        # Clear any previous seat selections for this user
        SelectedSeat.objects.filter(user=user).delete()
        
        # Create SelectedSeat records for held seats
        for seat in held_seats:
            SelectedSeat.objects.create(seat=seat, user=user, price=seat.price)
        
        # Broadcast seat holds to all clients
        cls._broadcast_seat_updates([s.seat_number for s in held_seats], 'held', user.id)
        
        return True, f"Successfully held {len(held_seats)} seats", held_seats
    
    @classmethod
    @transaction.atomic  
    def release_user_holds(cls, user):
        """Release ONLY held seats for a specific user - preserve booked seats"""
        held_seats = Seat.objects.select_for_update().filter(
            reserved_by=user, 
            status='held'
        )
        
        released_seat_numbers = []
        for seat in held_seats:
            released_seat_numbers.append(seat.seat_number)
            seat.release_hold()
        
        # Remove ONLY SelectedSeat records for HELD seats (not booked seats)
        held_seat_ids = [seat.id for seat in held_seats]
        SelectedSeat.objects.filter(user=user, seat__id__in=held_seat_ids).delete()
        
        if released_seat_numbers:
            cls._broadcast_seat_updates(released_seat_numbers, 'available', user.id)
        
        return released_seat_numbers
    
    @classmethod
    @transaction.atomic
    def convert_holds_to_bookings(cls, user):
        """Convert all held seats for a user to actual bookings"""
        held_seats = Seat.objects.select_for_update().filter(
            reserved_by=user,
            status='held'
        )
        
        if not held_seats.exists():
            return False, "No seats are currently held for this user"
        
        # Check if any holds have expired
        expired_seats = []
        valid_seats = []
        
        for seat in held_seats:
            if seat.reserved_until and timezone.now() > seat.reserved_until:
                expired_seats.append(seat.seat_number)
                seat.release_hold()
            else:
                valid_seats.append(seat)
        
        if expired_seats:
            return False, f"Hold expired for seats: {', '.join(expired_seats)}"
        
        # Convert holds to bookings
        booked_seats = []
        for seat in valid_seats:
            seat.book_seat()
            booked_seats.append(seat.seat_number)
        
        # Broadcast bookings
        cls._broadcast_seat_updates(booked_seats, 'booked', user.id)
        
        return True, f"Successfully booked {len(booked_seats)} seats"
    
    @classmethod
    def cleanup_expired_holds(cls):
        """Clean up all expired seat holds - called by management command"""
        expired_seats = Seat.objects.select_for_update().filter(
            status='held',
            reserved_until__lt=timezone.now()
        )
        
        released_seats = []
        for seat in expired_seats:
            released_seats.append(seat.seat_number)
            # Also clean up associated SelectedSeat records
            SelectedSeat.objects.filter(seat=seat, user=seat.reserved_by).delete()
            seat.release_hold()
        
        if released_seats:
            cls._broadcast_seat_updates(released_seats, 'available')
            print(f"Released {len(released_seats)} expired seat holds: {', '.join(released_seats)}")
        
        return len(released_seats)
    
    @classmethod
    def get_user_seat_status(cls, user):
        """Get current seat status for a user"""
        held_seats = Seat.objects.filter(reserved_by=user, status='held')
        selected_seats = SelectedSeat.objects.filter(user=user)
        
        status = {
            'held_seats': [],
            'selected_seats': [],
            'hold_expires_at': None
        }
        
        for seat in held_seats:
            status['held_seats'].append({
                'seat_number': seat.seat_number,
                'price': float(seat.price) if seat.price else 0,
                'expires_at': seat.reserved_until
            })
            if not status['hold_expires_at'] or seat.reserved_until < status['hold_expires_at']:
                status['hold_expires_at'] = seat.reserved_until
        
        for selected in selected_seats:
            status['selected_seats'].append({
                'seat_number': selected.seat.seat_number,
                'price': float(selected.price) if selected.price else 0
            })
        
        return status
    
    @classmethod
    def _broadcast_seat_updates(cls, seat_numbers, status, user_id=None):
        """Broadcast seat status updates via WebSocket"""
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'seat_updates',
            {
                'type': 'seat_status_update',
                'seats': seat_numbers,
                'status': status,
                'user_id': user_id
            }
        )
        print(f"[WebSocket] Broadcasting seats {status}: {seat_numbers} (user_id: {user_id})")