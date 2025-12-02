
from django.contrib import admin
from .models import Event, Seat, FormDetails, EventSelection, SeatSelection, PaymentScreenshot

class SeatAdmin(admin.ModelAdmin):
	search_fields = ['seat_number', 'event__name']

admin.site.register(Event)
admin.site.register(Seat, SeatAdmin)
admin.site.register(FormDetails)
admin.site.register(EventSelection)
admin.site.register(SeatSelection)
admin.site.register(PaymentScreenshot)
