from django.db import models


class LandingFormData(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    dob = models.DateField()
    submitted_at = models.DateTimeField(auto_now_add=True)

class PaymentScreenshot(models.Model):
    user = models.ForeignKey(LandingFormData, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    image = models.ImageField(upload_to='payment_screenshots/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Seat(models.Model):
    seat_number = models.CharField(max_length=10)
    is_booked = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    # Add more fields if needed for seat details

class SelectedSeat(models.Model):
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    user = models.ForeignKey(LandingFormData, on_delete=models.CASCADE)
    selected_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

# SIGNALS MUST BE AT THE END
from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=LandingFormData)
def unbook_seats_on_user_delete(sender, instance, **kwargs):
    print(f"Signal triggered: Deleting user {instance.id} and unbooking seats.")
    selected_seats = SelectedSeat.objects.filter(user=instance)
    for selected_seat in selected_seats:
        seat = selected_seat.seat
        # Delete the SelectedSeat for this user
        selected_seat.delete()
        # If no other SelectedSeat exists for this seat, unbook it
        if not SelectedSeat.objects.filter(seat=seat).exists():
            print(f"Unbooking seat: {seat.seat_number}")
            seat.is_booked = False
            seat.save()
