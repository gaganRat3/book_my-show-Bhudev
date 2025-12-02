
from django.shortcuts import render, redirect
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
	if request.method == 'POST':
		selected_seats = request.POST.getlist('selected_seats')
		user = LandingFormData.objects.get(id=user_id)
		for seat_num in selected_seats:
			seat, _ = Seat.objects.get_or_create(seat_number=seat_num)
			SelectedSeat.objects.create(seat=seat, user=user)
		return redirect('payment')
	seats = Seat.objects.all()
	return render(request, 'seat.html', {'seats': seats})

def payment(request):
	user_id = request.session.get('user_id')
	if not user_id:
		return redirect('landing_form')
	if request.method == 'POST':
		form = PaymentScreenshotForm(request.POST, request.FILES)
		if form.is_valid():
			PaymentScreenshot.objects.create(image=form.cleaned_data['image'])
			return render(request, 'payment.html', {'success': True})
	else:
		form = PaymentScreenshotForm()
	return render(request, 'payment.html', {'form': form})
