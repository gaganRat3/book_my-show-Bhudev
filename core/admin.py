from django.contrib import admin
from .models import LandingFormData, PaymentScreenshot, Seat, SelectedSeat

admin.site.register(LandingFormData)
admin.site.register(PaymentScreenshot)
admin.site.register(Seat)
admin.site.register(SelectedSeat)
