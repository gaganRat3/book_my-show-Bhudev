from django import forms

class LandingForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    phone = forms.CharField(max_length=15, required=True, label='Phone Number')
    dob = forms.DateField(required=True, label='Date of Birth', widget=forms.DateInput(attrs={'type': 'date'}))

class PaymentScreenshotForm(forms.Form):
    image = forms.ImageField(required=True)
