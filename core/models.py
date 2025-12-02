from django.db import models

class LandingFormData(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    dob = models.DateField()
    submitted_at = models.DateTimeField(auto_now_add=True)

class PaymentScreenshot(models.Model):
    image = models.ImageField(upload_to='payment_screenshots/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Seat(models.Model):
    seat_number = models.CharField(max_length=10)
    is_booked = models.BooleanField(default=False)
    # Add more fields if needed for seat details

class SelectedSeat(models.Model):
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    user = models.ForeignKey(LandingFormData, on_delete=models.CASCADE)
    selected_at = models.DateTimeField(auto_now_add=True)
