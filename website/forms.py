from django import forms
from .models import CustomUser, Transfer
from django.contrib.auth.hashers import make_password

class CustomUserUpdateForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=True,  
        label="New Password"
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=True,
        label="Confirm Password"
    )

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'phone', 'email',
            'street', 'city', 'state', 'country',
            'branch', 'account_type', 'category', 'password'
        ]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if not password or not confirm_password:
            raise forms.ValidationError("Password and Confirm Password are required.")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password']) 
        if commit:
            user.save()
        return user


class TransferForm(forms.ModelForm):
    class Meta:
        model = Transfer
        fields = ['from_user', 'to_user', 'amount', 'flow_direction']