# Payment confirmation view
def payment_confirmation(request):
	user_id = request.session.get('user_id')
	selected_seats = []
	if user_id:
		try:
			user = LandingFormData.objects.get(id=user_id)
			# Get all seats associated with this user (both booked and any remaining selected)
			selected_seats = [s.seat.seat_number for s in SelectedSeat.objects.filter(user=user)]
			print(f"[Payment Confirmation] User {user.name} has {len(selected_seats)} seats: {selected_seats}")
		except LandingFormData.DoesNotExist:
			print(f"[Payment Confirmation] User ID {user_id} not found")
	
	# Add a parameter to clear session after showing confirmation
	if request.GET.get('clear_session') == 'true':
		request.session.flush()
		print("[Payment Confirmation] Session cleared after payment confirmation")
	
	context = {'selected_seats': selected_seats}
	if user_id:
		try:
			user = LandingFormData.objects.get(id=user_id)
			context['user'] = user
		except LandingFormData.DoesNotExist:
			pass
	return render(request, 'payment_confirmation.html', context)

from django.shortcuts import render, redirect
from django.db.models import Sum, Min, F, Value
from django.db.models.functions import Cast
from django.db import models
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from .forms import LandingForm, PaymentScreenshotForm
from .models import LandingFormData, PaymentScreenshot, Seat, SelectedSeat
from .seat_reservation_service import SeatReservationService

def go_home(request):
	"""Safe way to go home that preserves booked seats"""
	user_id = request.session.get('user_id')
	if user_id:
		try:
			user = LandingFormData.objects.get(id=user_id)
			# Release only held seats, preserve booked seats
			released_seats = SeatReservationService.release_user_holds(user)
			if released_seats:
				print(f"[Go Home] Released {len(released_seats)} held seats for user {user.name}")
			else:
				print(f"[Go Home] No held seats to release for user {user.name}")
		except LandingFormData.DoesNotExist:
			print(f"[Go Home] User ID {user_id} not found")
	
	# Clear session and redirect to home
	request.session.flush()
	return redirect('landing_form')

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
		# Redirect to landing form - users must register first
		return redirect('landing_form')
	
	try:
		user = LandingFormData.objects.get(id=user_id)
	except LandingFormData.DoesNotExist:
		# If session user doesn't exist, redirect to registration
		return redirect('landing_form')
	
	if request.method == 'POST':
		selected_seat_labels = request.POST.getlist('selected_seats')
		print("[DEBUG] Raw seat labels received:", selected_seat_labels)
		
		if not selected_seat_labels:
			return HttpResponse("Please select at least one seat.", status=400)
		
		# Release any previous holds for this user
		SeatReservationService.release_user_holds(user)
		
		# Normalize seat IDs
		from core.seat_utils import normalize_seat_id
		normalized_seats = []
		missing_seats = []
		
		for seat_num in selected_seat_labels:
			seat_num_clean = seat_num.strip()
			normalized_seat_id = normalize_seat_id(seat_num_clean)
			
			try:
				seat = Seat.objects.get(seat_number=normalized_seat_id)
				normalized_seats.append(normalized_seat_id)
			except Seat.DoesNotExist:
				missing_seats.append(normalized_seat_id)
		
		if missing_seats:
			return render(request, 'error_message.html', {
				'title': 'Seats Not Found',
				'message': 'The following seats do not exist in our system.',
				'unavailable_seats': missing_seats
			}, status=400)
		
		# Try to hold the seats
		success, message, held_seats = SeatReservationService.hold_seats(normalized_seats, user)
		
		if not success:
			# Extract seat numbers from the message if possible
			import re
			seat_match = re.search(r'Seats? ([\w\-,\s]+) are not available', message)
			unavailable_seats = []
			if seat_match:
				unavailable_seats = [s.strip() for s in seat_match.group(1).split(',')]
			
			return render(request, 'error_message.html', {
				'title': 'Seats Unavailable',
				'message': 'Sorry, the seats you selected are no longer available.',
				'unavailable_seats': unavailable_seats
			}, status=400)
		
		return redirect('payment')
	
	# GET request - show seat selection page
	seats = Seat.objects.all()
	
	# Clean up ONLY expired holds, never touch booked seats
	current_time = timezone.now()
	expired_holds = Seat.objects.filter(
		status='held',
		reserved_until__lt=current_time
	)
	
	expired_count = 0
	for expired_seat in expired_holds:
		# Only release if it's actually a hold, never a booked seat
		if expired_seat.status == 'held' and not expired_seat.is_booked:
			expired_seat.release_hold()
			expired_count += 1
	
	if expired_count > 0:
		print(f"[DEBUG] Auto-released {expired_count} expired holds on page load")
	
	# Get seats with different statuses  
	booked_seats = []
	held_seats = []
	user_held_seats = []
	
	# Refresh seats data after cleanup with explicit query
	seats = Seat.objects.all().order_by('seat_number')
	
	print(f"[DEBUG] Total seats queried: {len(seats)}")
	print(f"[DEBUG] Current user: {user.name} (ID: {user.id})")
	
	# First, get ALL truly booked seats (some historical records might only set one flag)
	definitely_booked = Seat.objects.filter(
		models.Q(status='booked') | models.Q(is_booked=True)
	).distinct()
	print(f"[DEBUG] Found {len(definitely_booked)} definitely booked seats in database")
	
	for seat in definitely_booked:
		booked_seats.append(seat.seat_number)
		user_name = seat.reserved_by.name if seat.reserved_by else 'Unknown'
		print(f"[DEBUG] Added booked seat: {seat.seat_number} (booked by {user_name})")
	
	# Then process holds
	for seat in seats:
		if seat.status == 'held':
			# Double-check if hold is still valid
			if seat.reserved_until and current_time < seat.reserved_until:
				if seat.reserved_by == user:
					user_held_seats.append(seat.seat_number)
				else:
					held_seats.append(seat.seat_number)
			else:
				# This hold should have been cleaned up above, but just in case
				print(f"[DEBUG] Found stale hold on {seat.seat_number}, cleaning up")
				seat.release_hold()
	
	# Get user's current seat status
	user_seat_status = SeatReservationService.get_user_seat_status(user)
	
	print(f"[DEBUG] FINAL COUNTS:")
	print(f"[DEBUG]   Booked seats: {len(booked_seats)} - {booked_seats}")
	print(f"[DEBUG]   Held seats: {len(held_seats)} - {held_seats}")
	print(f"[DEBUG]   User held seats: {len(user_held_seats)} - {user_held_seats}")
	
	import json
	seat_prices = {seat.seat_number: float(seat.price) if seat.price else 0 for seat in seats}
	
	# Prepare user_seat_status for JSON serialization (convert datetime objects)
	held_seats_json = []
	for seat in user_seat_status['held_seats']:
		held_seats_json.append({
			'seat_number': seat['seat_number'],
			'price': seat['price'],
			'expires_at': seat['expires_at'].isoformat() if seat.get('expires_at') else None
		})
	
	user_seat_status_json = {
		'held_seats': held_seats_json,
		'selected_seats': user_seat_status['selected_seats'],
		'hold_expires_at': user_seat_status['hold_expires_at'].isoformat() if user_seat_status['hold_expires_at'] else None
	}
	
	context = {
		'seats': seats,
		'seat_prices': json.dumps(seat_prices),
		'booked_seats': json.dumps(booked_seats),
		'held_seats': json.dumps(held_seats),
		'user_held_seats': json.dumps(user_held_seats),
		'user_seat_status': json.dumps(user_seat_status_json),
		'hold_duration_minutes': SeatReservationService.HOLD_DURATION_MINUTES,
		'current_user_id': user.id,
	}
	
	return render(request, 'seat.html', context)

def payment(request):
	user_id = request.session.get('user_id')
	if not user_id:
		return redirect('landing_form')
	
	try:
		user = LandingFormData.objects.get(id=user_id)
	except LandingFormData.DoesNotExist:
		return redirect('landing_form')
	
	# Check if user has any held seats
	user_status = SeatReservationService.get_user_seat_status(user)
	if not user_status['held_seats']:
		return redirect('seat_selection')
	
	# Check if holds have expired
	if user_status['hold_expires_at'] and timezone.now() > user_status['hold_expires_at']:
		return HttpResponse("Your seat reservation has expired. Please select seats again.", status=400)
	
	if request.method == 'POST':
		form = PaymentScreenshotForm(request.POST, request.FILES)
		if form.is_valid():
			# Try to convert holds to actual bookings
			success, message = SeatReservationService.convert_holds_to_bookings(user)
			
			if not success:
				return HttpResponse(f"Booking failed: {message}", status=400)
			
			# Create payment screenshot record
			PaymentScreenshot.objects.create(user=user, image=form.cleaned_data['image'])
			print(f"[Payment Confirmed] {message}")
			
			return redirect('payment_confirmation')
	else:
		form = PaymentScreenshotForm()
	
	# Calculate total amount and time remaining
	total_amount = sum(seat['price'] for seat in user_status['held_seats'])
	time_remaining = None
	if user_status['hold_expires_at']:
		time_remaining = (user_status['hold_expires_at'] - timezone.now()).total_seconds()
	
	# Prepare held_seats for JSON serialization (remove datetime objects)
	held_seats_for_template = []
	for seat in user_status['held_seats']:
		held_seats_for_template.append({
			'seat_number': seat['seat_number'],
			'price': seat['price']
		})
	
	import json
	context = {
		'form': form,
		'held_seats': json.dumps(held_seats_for_template),
		'total_amount': total_amount,
		'time_remaining_seconds': max(0, int(time_remaining)) if time_remaining else 0,
		'hold_expires_at': user_status['hold_expires_at'],
		'user': user,
	}
	
	return render(request, 'payment.html', context)

# Booking report view: group by user, aggregate seat numbers
from django.db.models import Func

class GroupConcat(Func):
	function = 'GROUP_CONCAT'
	template = '%(function)s(%(expressions)s)'

def booking_report(request):
	search = request.GET.get('search', '').strip()
	qs = SelectedSeat.objects.values('user__name', 'user__phone').annotate(
		seats=GroupConcat('seat__seat_number'),
		total_paid=Sum('price'),
		selected_at=Min('selected_at')
	).order_by('user__name')
	if search:
		qs = qs.filter(
			models.Q(user__name__icontains=search) |
			models.Q(user__phone__icontains=search) |
			models.Q(seat__seat_number__icontains=search)
		)
	from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
	page = request.GET.get('page', 1)
	paginator = Paginator(qs, 10)  # Paginate queryset directly
	try:
		paginated_qs = paginator.page(page)
	except PageNotAnInteger:
		paginated_qs = paginator.page(1)
	except EmptyPage:
		paginated_qs = paginator.page(paginator.num_pages)
	final_report = []
	for row in paginated_qs:
		# Get user id for links
		user_obj = LandingFormData.objects.filter(name=row['user__name'], phone=row['user__phone']).first()
		user_id = user_obj.id if user_obj else ''
		final_report.append({
			'user': row['user__name'],
			'phone': row['user__phone'],
			'seats': row['seats'],
			'total_paid': row['total_paid'],
			'selected_at': row['selected_at'],
			'id': user_id,
		})
	return render(request, 'admin/booking_report.html', {
		'report': final_report,
		'search': search,
		'paginator': paginator,
		'page_obj': paginated_qs,
	})
