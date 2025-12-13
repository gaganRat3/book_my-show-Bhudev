from django.db import models
from django.utils import timezone
from datetime import timedelta


class LandingFormData(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(default="unknown@example.com")
    dob = models.DateField()
    submitted_at = models.DateTimeField(auto_now_add=True)

class PaymentScreenshot(models.Model):
    user = models.ForeignKey(LandingFormData, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    image = models.ImageField(upload_to='payment_screenshots/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Seat(models.Model):
    SEAT_STATUS_CHOICES = [
        ('available', 'Available'),
        ('held', 'Temporarily Held'),
        ('booked', 'Booked'),
    ]
    
    seat_number = models.CharField(max_length=10)
    is_booked = models.BooleanField(default=False)  # Keep for backward compatibility
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # New reservation fields
    status = models.CharField(max_length=20, choices=SEAT_STATUS_CHOICES, default='available')
    reserved_until = models.DateTimeField(null=True, blank=True)
    reserved_by = models.ForeignKey(LandingFormData, on_delete=models.SET_NULL, null=True, blank=True, related_name='held_seats')
    
    def is_available(self):
        """Check if seat is truly available"""
        if self.status == 'booked' or self.is_booked:
            return False
        if self.status == 'held' and self.reserved_until and timezone.now() < self.reserved_until:
            return False
        # If hold expired, automatically release it
        if self.status == 'held' and self.reserved_until and timezone.now() >= self.reserved_until:
            self.release_hold()
        return True
    
    def hold_for_user(self, user, minutes=10):
        """Hold seat for specified user and duration"""
        if not self.is_available():
            return False
        self.status = 'held'
        self.reserved_until = timezone.now() + timedelta(minutes=minutes)
        self.reserved_by = user
        self.save()
        return True
    
    def release_hold(self):
        """Release the hold on this seat - ONLY if it's actually held, never booked"""
        if self.is_booked or self.status == 'booked':
            print(f"[WARNING] Attempted to release hold on BOOKED seat {self.seat_number}! Ignoring.")
            return
        
        self.status = 'available'
        self.reserved_until = None
        self.reserved_by = None
        self.save()
    
    def book_seat(self):
        """Convert held seat to booked"""
        self.status = 'booked'
        self.is_booked = True
        self.reserved_until = None
        # Keep reserved_by for tracking who booked it
        self.save()
    
    def __str__(self):
        return f"Seat {self.seat_number} - {self.status}"

class SelectedSeat(models.Model):
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    user = models.ForeignKey(LandingFormData, on_delete=models.CASCADE)
    selected_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

# SIGNALS MUST BE AT THE END
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
# COMMENTED OUT FOR AJAX POLLING (NO WEBSOCKETS)
# from asgiref.sync import async_to_sync
# from channels.layers import get_channel_layer

# COMMENTED OUT - USING AJAX POLLING INSTEAD OF WEBSOCKETS
# @receiver(post_save, sender='core.Seat')
# def broadcast_seat_status_change(sender, instance, created, **kwargs):
#     """Broadcast seat status changes to all connected WebSocket clients"""
#     if not created:  # Only broadcast changes, not creation
#         channel_layer = get_channel_layer()
#         seat_numbers = [instance.seat_number]
#         
#         # Determine status for broadcasting
#         if instance.status == 'booked' or instance.is_booked:
#             status = 'booked'
#         elif instance.status == 'held':
#             status = 'held'
#         else:
#             status = 'available'
#         
#         async_to_sync(channel_layer.group_send)(
#             'seat_updates',
#             {
#                 'type': 'seat_status_update',
#                 'seats': seat_numbers,
#                 'status': status
#             }
#         )
#         print(f"[WebSocket] Broadcasting seat {status}: {seat_numbers}")

@receiver(post_delete, sender=LandingFormData)
def release_user_seats_on_delete(sender, instance, **kwargs):
    """Release ONLY held seats when user is deleted - NEVER unbook paid seats"""
    print(f"Signal triggered: Deleting user {instance.id} and releasing their HELD seats only.")
    
    # Release ONLY held seats (not booked seats)
    held_seats = Seat.objects.filter(reserved_by=instance, status='held')
    released_seat_numbers = []
    for seat in held_seats:
        released_seat_numbers.append(seat.seat_number)
        seat.release_hold()
        print(f"Released held seat: {seat.seat_number}")
    
    # Clean up SelectedSeat records but DO NOT unbook seats
    selected_seats = SelectedSeat.objects.filter(user=instance)
    for selected_seat in selected_seats:
        seat = selected_seat.seat
        # Only log booked seats, don't unbook them
        if seat.status == 'booked' or seat.is_booked:
            print(f"Keeping booked seat: {seat.seat_number} (payment completed)")
        selected_seat.delete()
    
    # COMMENTED OUT - USING AJAX POLLING INSTEAD OF WEBSOCKETS
    # # Broadcast ONLY released held seats
    # if released_seat_numbers:
    #     channel_layer = get_channel_layer()
    #     async_to_sync(channel_layer.group_send)(
    #         'seat_updates',
    #         {
    #             'type': 'seat_status_update',
    #             'seats': released_seat_numbers,
    #             'status': 'available'
    #         }
    #     )
    #     print(f"[WebSocket] Broadcasting held seats released: {released_seat_numbers}")
    
    print(f"User {instance.id} deletion complete - booked seats preserved.")
