from django import forms
from core.models import SelectedSeat, Seat

class LandingForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    phone = forms.CharField(max_length=15, required=True, label='Phone Number')
    email = forms.EmailField(required=True, label='Email')
    dob = forms.DateField(
        required=True,
        label='Date of Birth',
        widget=forms.TextInput(),
        input_formats=['%d-%m-%Y']
    )

class PaymentScreenshotForm(forms.Form):
    image = forms.ImageField(required=True)


class SelectedSeatEditForm(forms.Form):
    seats = forms.ModelMultipleChoiceField(queryset=Seat.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    total_paid = forms.DecimalField(max_digits=8, decimal_places=2, required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            selected_seats = SelectedSeat.objects.filter(user=user)
            self.fields['seats'].initial = [s.seat.id for s in selected_seats]
            self.fields['total_paid'].initial = sum(float(s.price or 0) for s in selected_seats)
