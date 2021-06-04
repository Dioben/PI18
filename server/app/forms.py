from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.contrib.auth import password_validation, forms as auth_forms
from django.utils.translation import gettext, gettext_lazy as _
from app.models import User


class SimCreationForm(forms.Form):
    model = forms.FileField(
        label='Model',
        widget=forms.FileInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    name = forms.CharField(
        max_length=100,
        label='Name',
        widget=forms.TextInput(
            attrs={
                'autofocus': True,
                'class': 'form-control'
            }
        )
    )
    max_epochs = forms.IntegerField(
        validators=[MinValueValidator(1)],
        label='Total epochs',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
            }
        )
    )
    logging_interval = forms.IntegerField(
        validators=[MinValueValidator(1)],
        label='Epoch period',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    batch_size = forms.IntegerField(
        validators=[MinValueValidator(1)],
        label='Batch size',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    learning_rate = forms.FloatField(
        validators=[MinValueValidator(0.00001)],
        label='Learning rate',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
            }
        )
    )
    train_dataset = forms.FileField(
        label='Training dataset',
        widget=forms.FileInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    test_dataset = forms.FileField(
        label='Test dataset',
        widget=forms.FileInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    val_dataset = forms.FileField(
        label='Validation dataset',
        widget=forms.FileInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    metrics = forms.MultipleChoiceField(
        label='Extra metrics',
        widget=forms.SelectMultiple(),
        choices=(
            ('AUC', 'AUC'),
            ('Accuracy', 'Accuracy'),
            ('BinaryAccuracy', 'BinaryAccuracy'),
            ('BinaryCrossentropy', 'BinaryCrossentropy'),
            ('CategoricalAccuracy', 'CategoricalAccuracy'),
            ('CategoricalCrossentropy', 'CategoricalCrossentropy'),
            ('CategoricalHinge', 'CategoricalHinge'),
            ('CosineSimilarity', 'CosineSimilarity'),
            ('FalseNegatives', 'FalseNegatives'),
            ('FalsePositives', 'FalsePositives'),
            ('Hinge', 'Hinge'),
            ('KLDivergence', 'KLDivergence'),
            ('LogCoshError', 'LogCoshError'),
            ('Mean', 'Mean'),
            ('MeanAbsoluteError', 'MeanAbsoluteError'),
            ('MeanAbsolutePercentageError', 'MeanAbsolutePercentageError'),
            ('MeanIoU', 'MeanIoU'),
            ('MeanRelativeError', 'MeanRelativeError'),
            ('MeanSquaredError', 'MeanSquaredError'),
            ('MeanSquaredLogarithmicError', 'MeanSquaredLogarithmicError'),
            ('MeanTensor', 'MeanTensor'),
            ('Poisson', 'Poisson'),
            ('Precision', 'Precision'),
            ('PrecisionAtRecall', 'PrecisionAtRecall'),
            ('Recall', 'Recall'),
            ('RecallAtPrecision', 'RecallAtPrecision'),
            ('RootMeanSquaredError', 'RootMeanSquaredError'),
            ('SensitivityAtSpecificity', 'SensitivityAtSpecificity'),
            ('SparseCategoricalAccuracy', 'SparseCategoricalAccuracy'),
            ('SparseCategoricalCrossentropy', 'SparseCategoricalCrossentropy'),
            ('SparseTopKCategoricalAccuracy', 'SparseTopKCategoricalAccuracy'),
            ('SpecificityAtSensitivity', 'SpecificityAtSensitivity'),
            ('SquaredHinge', 'SquaredHinge'),
            ('Sum', 'Sum'),
            ('TopKCategoricalAccuracy', 'TopKCategoricalAccuracy'),
            ('TrueNegatives', 'TrueNegatives'),
            ('TruePositives', 'TruePositives'),
        ),
        required=False
    )
    optimizer = forms.ChoiceField(
        label='Optimizer',
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }),
        choices=(
            ('Adadelta', 'Adadelta'),
            ('Adagrad', 'Adagrad'),
            ('Adam', 'Adam'),
            ('Adamax', 'Adamax'),
            ('Ftrl', 'Ftrl'),
            ('Nadam', 'Nadam'),
            ('RMSprop', 'RMSprop'),
            ('SGD', 'SGD'),
        )
    )
    loss_function = forms.ChoiceField(
        label='Loss function',
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }),
        choices=(
            ('BinaryCrossentropy', 'BinaryCrossentropy'),
            ('CategoricalCrossentropy', 'CategoricalCrossentropy'),
            ('CategoricalHinge', 'CategoricalHinge'),
            ('CosineSimilarity', 'CosineSimilarity'),
            ('Hinge', 'Hinge'),
            ('Huber', 'Huber'),
            ('KLDivergence', 'KLDivergence'),
            ('LogCosh', 'LogCosh'),
            ('MeanAbsoluteError', 'MeanAbsoluteError'),
            ('MeanAbsolutePercentageError', 'MeanAbsolutePercentageError'),
            ('MeanSquaredError', 'MeanSquaredError'),
            ('MeanSquaredLogarithmicError', 'MeanSquaredLogarithmicError'),
            ('Poisson', 'Poisson'),
            ('Reduction', 'Reduction'),
            ('SparseCategoricalCrossentropy', 'SparseCategoricalCrossentropy'),
            ('SquaredHinge', 'SquaredHinge'),
        )
    )
    is_k_fold = forms.BooleanField(
        label='K-Fold cross-validation',
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input',
            }
        )
    )
    k_fold_validation = forms.IntegerField(
        label='K-Fold splits',
        validators=[MinValueValidator(2)],
        required=False,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    tag = forms.CharField(
        label='K-Fold tag',
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    def clean_logging_interval(self):
        cleaned_data = super().clean()
        clean_logging_interval = cleaned_data.get("logging_interval")
        if clean_logging_interval > cleaned_data.get("max_epochs"):
            raise ValidationError("Logging interval is larger than total runtime")
        return clean_logging_interval

    def clean_k_fold_validation(self):
        cleaned_data = super().clean()
        clean_k_fold_validation = cleaned_data.get("k_fold_validation")
        if cleaned_data.get("is_k_fold") and clean_k_fold_validation is None:
            raise ValidationError("K-Fold needs to have splits set")
        return clean_k_fold_validation

    def clean_tag(self):
        cleaned_data = super().clean()
        clean_tag = cleaned_data.get("tag")
        if cleaned_data.get("is_k_fold") and (clean_tag is None or str(clean_tag).strip() == ''):
            raise ValidationError("K-Fold needs to have tag set")
        return clean_tag


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
