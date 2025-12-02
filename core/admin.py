
from django.contrib import admin
from .models import LandingFormData, PaymentScreenshot, Seat, SelectedSeat

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
	list_display = ('seat_number', 'is_booked')

admin.site.register(LandingFormData)
admin.site.register(PaymentScreenshot)

@admin.register(SelectedSeat)
class SelectedSeatAdmin(admin.ModelAdmin):
	list_display = ('get_user_name', 'get_seat_labels', 'selected_at')

	def get_user_name(self, obj):
		return obj.user.name
	get_user_name.short_description = 'User Name'

	def get_seat_labels(self, obj):
		# Get all seats selected by this user
		seats = SelectedSeat.objects.filter(user=obj.user).values_list('seat__seat_number', flat=True)
		return ', '.join(seats)
	get_seat_labels.short_description = 'Seats'
