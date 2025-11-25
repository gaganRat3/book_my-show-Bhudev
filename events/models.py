from django.db import models
class FormDetails(models.Model):
	name = models.CharField(max_length=100)
	phone = models.CharField(max_length=15)
	dob = models.DateField()
	def __str__(self):
		return f"{self.name} ({self.phone})"

class EventSelection(models.Model):
	user = models.ForeignKey(FormDetails, on_delete=models.CASCADE, related_name='event_selections')
	event = models.ForeignKey('Event', on_delete=models.CASCADE)
	def __str__(self):
		return f"{self.user.name} - {self.event.name}"

class SeatSelection(models.Model):
	event_selection = models.ForeignKey(EventSelection, on_delete=models.CASCADE, related_name='seat_selections')
	seat = models.ForeignKey('Seat', on_delete=models.CASCADE)
	def __str__(self):
		return f"{self.event_selection.user.name} - {self.seat.seat_number} ({self.event_selection.event.name})"

class PaymentScreenshot(models.Model):
	event_selection = models.ForeignKey(EventSelection, on_delete=models.CASCADE, related_name='payment_screenshots')
	screenshot = models.ImageField(upload_to='payment_screenshots/')
	uploaded_at = models.DateTimeField(auto_now_add=True)
	def __str__(self):
		return f"Payment for {self.event_selection.user.name} - {self.event_selection.event.name}"
from django.db import models

class Event(models.Model):
	name = models.CharField(max_length=200)
	description = models.TextField()
	date = models.DateTimeField()
	location = models.CharField(max_length=200)

	def __str__(self):
		return self.name


class Booking(models.Model):
	whatsapp_number = models.CharField(max_length=20)
	qr_code = models.ImageField(upload_to='qr_codes/')
	payment_screenshot = models.ImageField(upload_to='payment_screenshots/')
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Booking {self.whatsapp_number} at {self.created_at}" 


# Added Seat model
class Seat(models.Model):
	event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='seats')
	seat_number = models.CharField(max_length=10)
	is_booked = models.BooleanField(default=False)

	def __str__(self):
		return f"Seat {self.seat_number} for {self.event.name}"
