
from django.contrib import admin
from .models import LandingFormData, PaymentScreenshot, Seat, SelectedSeat

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
	list_display = ('seat_number', 'is_booked')

admin.site.register(LandingFormData)
admin.site.register(PaymentScreenshot)
admin.site.register(SelectedSeat)
