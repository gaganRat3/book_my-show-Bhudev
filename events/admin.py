from django.contrib import admin
from .models import Event, Seat, FormDetails, EventSelection, SeatSelection, PaymentScreenshot

admin.site.register(Event)
admin.site.register(Seat)
admin.site.register(FormDetails)
admin.site.register(EventSelection)
admin.site.register(SeatSelection)
admin.site.register(PaymentScreenshot)
