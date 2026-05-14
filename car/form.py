from django import forms
from .models import BookingModel, Location
from django.utils import timezone
from datetime import datetime

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class BookingForm(forms.ModelForm):
    pickup_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    pickup_time = forms.TimeField(widget=forms.TimeInput(attrs={"type": "time"}))

    return_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    return_time = forms.TimeField(widget=forms.TimeInput(attrs={"type": "time"}))

    class Meta:
        model = BookingModel
        fields = ["location"]

    def clean(self):
        cleaned = super().clean()

        pickup_date = cleaned.get("pickup_date")
        pickup_time = cleaned.get("pickup_time")
        return_date = cleaned.get("return_date")
        return_time = cleaned.get("return_time")

        if not all([pickup_date, pickup_time, return_date, return_time]):
            return cleaned

        pickup_datetime = timezone.make_aware(
            datetime.combine(pickup_date, pickup_time)
        )
        return_datetime = timezone.make_aware(
            datetime.combine(return_date, return_time)
        )

        if pickup_datetime < timezone.now():
            raise forms.ValidationError("Pickup cannot be in the past")

        if return_datetime <= pickup_datetime:
            raise forms.ValidationError("Return must be after pickup")

        cleaned["pickup_datetime"] = pickup_datetime
        cleaned["return_datetime"] = return_datetime

        return cleaned

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "Enter your email"}),
    )

    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={"placeholder": "Enter username"}),
    )

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Enter password"}),
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm your password"}),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # remove ugly help text
        for field in self.fields:
            self.fields[field].help_text = None
