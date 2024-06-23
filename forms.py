from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from apps.APyme.models import Profile, Unidad

User = get_user_model()


class RegisterUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    # Check unique email
    # Email exists && account active -> email_already_registered
    # Email exists && account not active -> delete previous account and register new one
    def clean_email(self):
        email_passed = self.cleaned_data.get("email")
        email_already_registered = User.objects.filter(email=email_passed).exists()
        user_is_active = User.objects.filter(email=email_passed, is_active=1)
        if email_already_registered and user_is_active:
            raise forms.ValidationError("Este correo ya está registrado.")
        # elif email_already_registered:
        #     User.objects.filter(email=email_passed).delete()

        return email_passed


class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email']


class UpdateProfileForm(forms.ModelForm):
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))

    class Meta:
        model = Profile
        fields = ['logo', 'bio']


class UnidadMedidaForm(forms.ModelForm):
    class Meta:
        model = Unidad
        fields = ['unidad']
