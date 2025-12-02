
from django import forms


class LandingForm(forms.Form):
	name = forms.CharField(max_length=100, required=True)
	phone = forms.CharField(max_length=15, required=True, label='Phone Number')
	dob = forms.DateField(required=True, label='Date of Birth', widget=forms.DateInput(attrs={'type': 'date'}))

def landing_form(request):
	import sys
	if request.method == 'POST':
		print('DEBUG: Landing form submitted', file=sys.stderr)
		form = LandingForm(request.POST)
		if form.is_valid():
			print('DEBUG: Landing form is valid', file=sys.stderr)
			# No database save, just show seat page
			return render(request, 'seat.html')
		else:
			print('DEBUG: Landing form is invalid', file=sys.stderr)
	else:
		form = LandingForm()
	return render(request, 'landing_form.html', {'form': form})
from django.shortcuts import render




