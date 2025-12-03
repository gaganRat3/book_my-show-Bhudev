from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.template import loader
from core.models import SelectedSeat, LandingFormData

class SelectedSeatSummaryAdmin(admin.ModelAdmin):
	def get_urls(self):
		urls = super().get_urls()
		custom_urls = [
			path('selectedseat-summary/', self.admin_site.admin_view(self.selectedseat_summary_view), name="selectedseat-summary"),
			path('selectedseat-summary/edit/<int:user_id>/', self.admin_site.admin_view(self.edit_selectedseat_view), name="edit-selectedseat"),
		]
		return custom_urls + urls
	def edit_selectedseat_view(self, request, user_id):
		from core.forms import SelectedSeatEditForm
		user = LandingFormData.objects.get(id=user_id)
		if request.method == 'POST':
			form = SelectedSeatEditForm(request.POST, request.FILES, user=user)
			if form.is_valid():
				# Update selected seats
				SelectedSeat.objects.filter(user=user).delete()
				for seat in form.cleaned_data['seats']:
					SelectedSeat.objects.create(user=user, seat=seat, price=seat.price)
				# Optionally update total_paid (if you want to store it elsewhere)
				from django.urls import reverse
				return redirect(reverse('admin:selectedseat-summary'))
		else:
			form = SelectedSeatEditForm(user=user)
		template = loader.get_template("admin/edit_selectedseat.html")
		context = {"form": form, "back_url": "/admin/core/landingformdata/selectedseat-summary/"}
		return HttpResponse(template.render(context, request))

	def selectedseat_summary_view(self, request):
		users = LandingFormData.objects.all()
		report = []
		for user in users:
				seats = SelectedSeat.objects.filter(user=user)
				seat_labels = [s.seat.seat_number for s in seats]
				total_paid = sum(float(s.price or 0) for s in seats)
				earliest = seats.order_by('selected_at').first().selected_at if seats.exists() else None
				report.append({
					'id': user.id,
					'user': user.name,
					'phone': user.phone,
					'seats': ', '.join(seat_labels),
					'total_paid': total_paid,
					'selected_at': earliest,
				})
		template = loader.get_template("admin/selectedseat_summary.html")
		context = {"report": report}
		return HttpResponse(template.render(context, request))

admin.site.register_view = lambda name, view, url=None: admin.site.get_urls().insert(0, path(url or name + '/', view, name=name))
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.template import loader
from core.models import SelectedSeat, LandingFormData

class BookingReportAdmin(admin.ModelAdmin):
	change_list_template = "admin/booking_report.html"

	def get_urls(self):
		urls = super().get_urls()
		custom_urls = [
			path('booking-report/', self.admin_site.admin_view(self.booking_report_view), name="booking-report"),
		]
		return custom_urls + urls

	def booking_report_view(self, request):
		# Aggregate booking info per user
			users = LandingFormData.objects.all()
			report = []
			for user in users:
				seats = SelectedSeat.objects.filter(user=user)
				seat_labels = [s.seat.seat_number for s in seats]
				total_paid = sum(float(s.price or 0) for s in seats)
				earliest = seats.order_by('selected_at').first().selected_at if seats.exists() else None
				report.append({
					'id': user.id,
					'user': user.name,
					'phone': user.phone,
					'seats': ', '.join(seat_labels),
					'total_paid': total_paid,
					'selected_at': earliest,
				})
			template = loader.get_template("admin/booking_report.html")
			context = {"report": report}
			return HttpResponse(template.render(context, request))

## Removed lambda-based admin.site.register_view code

from django.contrib import admin
from .models import LandingFormData, PaymentScreenshot, Seat, SelectedSeat

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
	list_display = ('seat_number', 'is_booked')

## Removed duplicate registration for LandingFormData; now only registered with SelectedSeatSummaryAdmin
admin.site.register(PaymentScreenshot)




## Removed default SelectedSeatAdmin registration to avoid duplicate user rows
admin.site.register(LandingFormData, SelectedSeatSummaryAdmin)
