import os
from django.conf import settings
from .forms import PaymentScreenshotForm
def payment(request):
	uploaded_url = None
	if request.method == 'POST':
		form = PaymentScreenshotForm(request.POST, request.FILES)
		if form.is_valid():
			screenshot = form.cleaned_data['screenshot']
			upload_dir = os.path.join(settings.MEDIA_ROOT, 'payments')
			os.makedirs(upload_dir, exist_ok=True)
			file_path = os.path.join(upload_dir, screenshot.name)
			with open(file_path, 'wb+') as destination:
				for chunk in screenshot.chunks():
					destination.write(chunk)
			uploaded_url = settings.MEDIA_URL + 'payments/' + screenshot.name
	return render(request, 'payment.html', {'uploaded_url': uploaded_url})
from django import forms


class LandingForm(forms.Form):
	name = forms.CharField(max_length=100, required=True)
	phone = forms.CharField(max_length=15, required=True, label='Phone Number')
	dob = forms.DateField(required=True, label='Date of Birth', widget=forms.DateInput(attrs={'type': 'date'}))

def landing_form(request):
	if request.method == 'POST':
		form = LandingForm(request.POST)
		if form.is_valid():
			# You can save or process form data here
			return redirect('event_list')
	else:
		form = LandingForm()
	return render(request, 'landing_form.html', {'form': form})
from django.shortcuts import render, get_object_or_404
from .models import Event, Seat

def event_list(request):
	events = Event.objects.all()
	if not events:
		# Add sample events if none exist
		Event.objects.create(
			name='Rock Concert',
			description='Enjoy a night of rock music with top bands.',
			date='2025-12-10 19:00',
			location='City Arena'
		)
		Event.objects.create(
			name='Stand-up Comedy',
			description='Laugh out loud with the best comedians.',
			date='2025-12-15 20:00',
			location='Comedy Club'
		)
		Event.objects.create(
			name='Movie Premiere',
			description='Be the first to watch the latest blockbuster.',
			date='2025-12-20 18:30',
			location='Grand Cinema'
		)
		events = Event.objects.all()
	return render(request, 'event_list.html', {'events': events})

def event_detail(request, event_id):
	event = get_object_or_404(Event, pk=event_id)
	seats = event.seats.all()
	return render(request, 'event_detail.html', {'event': event, 'seats': seats})

from django.http import JsonResponse
def seat_selection(request, event_id):
	event = get_object_or_404(Event, pk=event_id)
	seats = event.seats.all()
	if request.method == 'POST':
		# Handle AJAX request
		if request.headers.get('x-requested-with') == 'XMLHttpRequest':
			import json
			data = json.loads(request.body)
			selected_seats = data.get('selected_seats', [])
			booked = []
			failed = []
			for seat_id in selected_seats:
				try:
					seat = Seat.objects.get(seat_number=seat_id, event=event)
					if not seat.is_booked:
						seat.is_booked = True
						seat.save()
						booked.append(seat_id)
					else:
						failed.append(seat_id)
				except Seat.DoesNotExist:
					failed.append(seat_id)
			return JsonResponse({'success': True, 'booked': booked, 'failed': failed})
		else:
			selected_seats = request.POST.getlist('selected_seats')
			for seat_id in selected_seats:
				seat = Seat.objects.get(id=seat_id, event=event)
				if not seat.is_booked:
					seat.is_booked = True
					seat.save()
			return render(request, 'seat.html', {'event': event, 'seats': seats, 'success': True})
	return render(request, 'seat.html', {'event': event, 'seats': seats})


from django.shortcuts import redirect
from django import forms

class EventForm(forms.ModelForm):
	class Meta:
		model = Event
		fields = ['name', 'description', 'date', 'location']

def add_event(request):
	if request.method == 'POST':
		form = EventForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('event_list')
	else:
		form = EventForm()
	return render(request, 'add_event.html', {'form': form})
