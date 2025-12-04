# Payment confirmation view
def payment_confirmation(request):
		user_id = request.session.get('user_id')
		selected_seats = []
		if user_id:
			selected_seats = [s.seat.seat_number for s in SelectedSeat.objects.filter(user_id=user_id)]
		return render(request, 'payment_confirmation.html', {'selected_seats': selected_seats})

from django.shortcuts import render, redirect
from django.db.models import Sum, Min, F, Value
from django.db.models.functions import Cast
from django.db import models
from .forms import LandingForm, PaymentScreenshotForm
from .models import LandingFormData, PaymentScreenshot, Seat, SelectedSeat

def landing_form(request):
	if request.method == 'POST':
		form = LandingForm(request.POST)
		if form.is_valid():
			user = LandingFormData.objects.create(
				name=form.cleaned_data['name'],
				phone=form.cleaned_data['phone'],
				dob=form.cleaned_data['dob']
			)
			request.session['user_id'] = user.id
			return redirect('seat_selection')
	else:
		form = LandingForm()
	return render(request, 'landing_form.html', {'form': form})

def seat_selection(request):
	user_id = request.session.get('user_id')
	if not user_id:
		return redirect('landing_form')
	try:
		user = LandingFormData.objects.get(id=user_id)
	except LandingFormData.DoesNotExist:
		return redirect('landing_form')
	if request.method == 'POST':
		selected_seat_labels = request.POST.getlist('selected_seats')
		print("[DEBUG] Raw seat labels received:", selected_seat_labels)
		from django.http import HttpResponse
		missing_seats = []
		# Clear any previous seat selections for this user
		SelectedSeat.objects.filter(user=user).delete()
		
		for seat_num in selected_seat_labels:
			seat_num_clean = seat_num.strip()
			try:
				# Use the exact data-id value for seat_number
				seat = Seat.objects.get(seat_number=seat_num_clean)
				# Check if seat is already booked by someone else
				if seat.is_booked:
					return HttpResponse(f"Seat {seat_num_clean} is already booked. Please refresh and select different seats.", status=400)
				# Save to SelectedSeat but DON'T mark is_booked yet (pending payment)
				SelectedSeat.objects.create(seat=seat, user=user, price=seat.price)
			except Seat.DoesNotExist:
				missing_seats.append(seat_num_clean)
		if missing_seats:
			# Log missing seats and show a friendly error
			return HttpResponse(f"The following seats do not exist: {', '.join(missing_seats)}", status=400)
		return redirect('payment')
	seats = Seat.objects.all()
	booked_seats = list(seats.filter(is_booked=True).values_list('seat_number', flat=True))
	print(f"[DEBUG] Booked seats being sent to template: {booked_seats}")
	import json
	seat_prices = {seat.seat_number: float(seat.price) if seat.price else 0 for seat in seats}
	seat_prices_json = json.dumps(seat_prices)
	booked_seats_json = json.dumps(booked_seats)
	return render(request, 'seat.html', {
		'seats': seats,
		'seat_prices': seat_prices_json,
		'booked_seats': booked_seats_json,
	})

def payment(request):
	user_id = request.session.get('user_id')
	if not user_id:
		return redirect('landing_form')
	if request.method == 'POST':
		form = PaymentScreenshotForm(request.POST, request.FILES)
		if form.is_valid():
			user = LandingFormData.objects.get(id=user_id)
			PaymentScreenshot.objects.create(user=user, image=form.cleaned_data['image'])
			
			# NOW mark seats as booked after payment is uploaded
			selected_seats = SelectedSeat.objects.filter(user=user)
			for selected_seat in selected_seats:
				seat = selected_seat.seat
				if not seat.is_booked:
					seat.is_booked = True
					seat.save()
					print(f"[Payment Confirmed] Seat {seat.seat_number} marked as booked")
			
			return redirect('payment_confirmation')
	else:
		form = PaymentScreenshotForm()
	return render(request, 'payment.html', {'form': form})

# Booking report view: group by user, aggregate seat numbers
from django.db.models import Func

class GroupConcat(Func):
	function = 'GROUP_CONCAT'
	template = '%(function)s(%(expressions)s)'

def booking_report(request):
	report = (
		SelectedSeat.objects
		.values('user__name', 'user__phone')
		.annotate(
			seats=GroupConcat('seat__seat_number'),
			total_paid=Sum('price'),
			selected_at=Min('selected_at')
		)
		.order_by('user__name')
	)
	# Prepare context for template
	final_report = []
	for row in report:
		final_report.append({
			'user': row['user__name'],
			'phone': row['user__phone'],
			'seats': row['seats'],
			'total_paid': row['total_paid'],
			'selected_at': row['selected_at'],
		})
	return render(request, 'admin/booking_report.html', {'report': final_report})
