from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordResetForm, UserCreationForm
from django.contrib.auth import get_user_model
import re

User = get_user_model()

GRADE_CHOICES = [
    ("", "Select your grade"),  # Added empty/default choice
    ("G10", "Grade 10"),
    ("G11", "Grade 11"),
    ("G12", "Grade 12"),
]

from .models import CourseOption

class SignUpForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Username",
            "autocomplete": "off"
        }),
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "your@email.com"
        })
    )

    age = forms.IntegerField(
        required=True,
        min_value=1,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Your age (optional)"
        }),
        help_text="Your age (optional)"
    )

    help_text = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "How can you help us? (optional)",
            "rows": 3
        }),
        label="How can you help us?",
        help_text="Tell us how you can help us (optional)"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'age', 'help_text', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to password fields
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def clean_username(self):
        username = self.cleaned_data.get('username', '').lower()
        if not re.match(r'^[\w.@+-]+$', username):
            raise ValidationError(
                "Username may only contain letters, numbers and @/./+/-/_ characters."
            )
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("This email is already registered.")
        return email
    


class StrictPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data["email"]
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise ValidationError("There is no active account with this email address.")
        return email

    def save(self, domain_override=None, request=None, **kwargs):
        # Remove use_https from kwargs if it exists to prevent duplication
        kwargs.pop('use_https', None)
        
        # Only proceed if there are active users
        email = self.cleaned_data["email"]
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            return None
            
        # Call parent save method with proper arguments
        return super().save(
            domain_override=domain_override,
            request=request,
            **kwargs
        )

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autocomplete': 'off'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'off'
        })
    )
