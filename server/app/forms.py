from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.contrib.auth import password_validation, forms as auth_forms
from django.utils.translation import gettext, gettext_lazy as _
from app.models import User


class UploadModelFileForm(forms.Form):
    # title = forms.CharField(max_length=50)
    model = forms.FileField(
        label='Select a Model',
        # widget=forms.FileInput(
        #     attrs={
        #         'class': 'form-control'
        #     }
        # )
    )


class UploadDataSetFileForm(forms.Form):
    # title = forms.CharField(max_length=50)
    dataset = forms.FileField(label='Select a DataSet')


class ConfSimForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        # widget=forms.TextInput(
        #     attrs={
        #         'autofocus': True,
        #         'class': 'form-control py-4'
        #     }
        # )
    )
    max_epochs = forms.IntegerField(
        validators=[MinValueValidator(1)],
        # widget=forms.NumberInput(
        #     attrs={
        #         'class': 'form-control'
        #     }
        # )
    )
    logging_interval = forms.IntegerField(
        validators=[MinValueValidator(1)],
        # widget=forms.NumberInput(
        #     attrs={
        #         'class': 'form-control'
        #     }
        # )
    )
    train_dataset_url = forms.URLField(
        # widget=forms.TextInput(
        #     attrs={
        #         'class': 'form-control py-4'
        #     }
        # )
    )
    test_dataset_url = forms.URLField(
        required=False,
        help_text="If absent we will use the training dataset",
        # widget=forms.TextInput(
        #     attrs={
        #         'class': 'form-control py-4'
        #     }
        # )
    )

    def clean_logging_interval(self):
        cleaned_data = super().clean()
        clean_logging_interval = cleaned_data.get("logging_interval")
        if clean_logging_interval > cleaned_data.get("max_epochs"):
            raise ValidationError("Logging interval is larger than total runtime")
        return clean_logging_interval


class CustomAuthenticationForm(auth_forms.AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)

    username = auth_forms.UsernameField(
        widget=forms.TextInput(
            attrs={
                'autofocus': True,
                'class': 'form-control'
            }
        )
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'current-password',
                'class': 'form-control'
            }
        ),
    )


class CustomUserCreationForm(auth_forms.UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'new-password',
                'class': 'form-control'
            }
        ),
        help_text="\n".join(password_validation.password_validators_help_texts()),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'new-password',
                'class': 'form-control'
            }
        ),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        model = User
        fields = ("username",)
        field_classes = {'username': auth_forms.UsernameField}
        widgets = {'username': forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )}
