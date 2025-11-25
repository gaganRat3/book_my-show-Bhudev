from django import forms

class PaymentScreenshotForm(forms.Form):
    screenshot = forms.ImageField(required=True)
