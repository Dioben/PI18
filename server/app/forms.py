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
    use_url_datasets = forms.BooleanField(
        label='Use links for the datasets',
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input',
            }
        )
    )
    train_dataset = forms.FileField(
        label='Training dataset',
        required=False,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    url_train_dataset = forms.URLField(
        max_length=255,
        label='Training dataset',
        required=False,
        widget=forms.URLInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    test_dataset = forms.FileField(
        label='Test dataset',
        required=False,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    url_test_dataset = forms.URLField(
        max_length=255,
        label='Test dataset',
        required=False,
        widget=forms.URLInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    val_dataset = forms.FileField(
        label='Validation dataset',
        required=False,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    url_val_dataset = forms.URLField(
        max_length=255,
        label='Validation dataset',
        required=False,
        widget=forms.URLInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    dataset_format = forms.ChoiceField(
        label='Format used by the datasets',
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }),
        choices=(
            ('npz', '.npz'),
            ('csv', '.csv'),
        )
    )
    label_column = forms.CharField(
        label='Label column',
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    train_feature_name = forms.CharField(
        label='Training feature name',
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    train_label_name = forms.CharField(
        label='Training label name',
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    test_feature_name = forms.CharField(
        label='Test feature name',
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    test_label_name = forms.CharField(
        label='Test label name',
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    val_feature_name = forms.CharField(
        label='Validation feature name',
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    val_label_name = forms.CharField(
        label='Validation label name',
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

    # def clean_train_dataset(self):
    #     cleaned_data = super().clean()
    #     clean_train_dataset = cleaned_data.get("train_dataset")
    #     if not cleaned_data.get("use_url_datasets"):
    #         if clean_train_dataset is None:
    #             raise ValidationError("Training dataset is required")
    #         if clean_train_dataset.name.split(".")[-1] != cleaned_data.get("dataset_format"):
    #             raise ValidationError("Please select the correct format below")
    #     return clean_train_dataset

    def clean_url_train_dataset(self):
        cleaned_data = super().clean()
        clean_url_train_dataset = cleaned_data.get("url_train_dataset")
        if cleaned_data.get("use_url_datasets") and (clean_url_train_dataset is None or str(clean_url_train_dataset).strip() == ''):
            raise ValidationError("Training dataset is required")
        return clean_url_train_dataset

    # def clean_test_dataset(self):
    #     cleaned_data = super().clean()
    #     clean_test_dataset = cleaned_data.get("test_dataset")
    #     if not cleaned_data.get("use_url_datasets"):
    #         if clean_test_dataset is None:
    #             raise ValidationError("Test dataset is required")
    #         if clean_test_dataset.name.split(".")[-1] != cleaned_data.get("dataset_format"):
    #             raise ValidationError("Please select the correct format below")
    #     return clean_test_dataset

    def clean_url_test_dataset(self):
        cleaned_data = super().clean()
        clean_url_test_dataset = cleaned_data.get("url_test_dataset")
        if cleaned_data.get("use_url_datasets") and (clean_url_test_dataset is None or str(clean_url_test_dataset).strip() == ''):
            raise ValidationError("Test dataset is required")
        return clean_url_test_dataset

    # def clean_val_dataset(self):
    #     cleaned_data = super().clean()
    #     clean_val_dataset = cleaned_data.get("val_dataset")
    #     if not cleaned_data.get("use_url_datasets"):
    #         if clean_val_dataset is None:
    #             raise ValidationError("Validation dataset is required")
    #         if clean_val_dataset.name.split(".")[-1] != cleaned_data.get("dataset_format"):
    #             raise ValidationError("Please select the correct format below")
    #     return clean_val_dataset

    def clean_url_val_dataset(self):
        cleaned_data = super().clean()
        clean_url_val_dataset = cleaned_data.get("url_val_dataset")
        if cleaned_data.get("use_url_datasets") and (clean_url_val_dataset is None or str(clean_url_val_dataset).strip() == ''):
            raise ValidationError("Validation dataset is required")
        return clean_url_val_dataset

    def clean_label_column(self):
        cleaned_data = super().clean()
        clean_label_column = cleaned_data.get("label_column")
        if cleaned_data.get("dataset_format") == "csv" and (clean_label_column is None or str(clean_label_column).strip() == ''):
            raise ValidationError("Label column is required")
        return clean_label_column

    def clean_train_feature_name(self):
        cleaned_data = super().clean()
        clean_train_feature_name = cleaned_data.get("train_feature_name")
        if cleaned_data.get("dataset_format") == "npz" and (clean_train_feature_name is None or str(clean_train_feature_name).strip() == ''):
            raise ValidationError("Training feature name is required")
        return clean_train_feature_name

    def clean_train_label_name(self):
        cleaned_data = super().clean()
        clean_train_label_name = cleaned_data.get("train_label_name")
        if cleaned_data.get("dataset_format") == "npz" and (clean_train_label_name is None or str(clean_train_label_name).strip() == ''):
            raise ValidationError("Training label name is required")
        return clean_train_label_name

    def clean_test_feature_name(self):
        cleaned_data = super().clean()
        clean_test_feature_name = cleaned_data.get("test_feature_name")
        if cleaned_data.get("dataset_format") == "npz" and (clean_test_feature_name is None or str(clean_test_feature_name).strip() == ''):
            raise ValidationError("Test feature name is required")
        return clean_test_feature_name

    def clean_test_label_name(self):
        cleaned_data = super().clean()
        clean_test_label_name = cleaned_data.get("test_label_name")
        if cleaned_data.get("dataset_format") == "npz" and (clean_test_label_name is None or str(clean_test_label_name).strip() == ''):
            raise ValidationError("Test label name is required")
        return clean_test_label_name

    def clean_val_feature_name(self):
        cleaned_data = super().clean()
        clean_val_feature_name = cleaned_data.get("val_feature_name")
        if cleaned_data.get("dataset_format") == "npz" and (clean_val_feature_name is None or str(clean_val_feature_name).strip() == ''):
            raise ValidationError("Validation feature name is required")
        return clean_val_feature_name

    def clean_val_label_name(self):
        cleaned_data = super().clean()
        clean_val_label_name = cleaned_data.get("val_label_name")
        if cleaned_data.get("dataset_format") == "npz" and (clean_val_label_name is None or str(clean_val_label_name).strip() == ''):
            raise ValidationError("Validation label name is required")
        return clean_val_label_name


class ConfigFileSimCreationForm(forms.Form):
    config = forms.FileField(
        label='Config',
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'id': 'file_id_config'
            }
        )
    )
    model = forms.FileField(
        label='Model',
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'id': 'file_id_model'
            }
        )
    )
    use_url_datasets = forms.BooleanField(
        label='Use links for the datasets',
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input',
                'id': 'file_use_url_datasets',
            }
        )
    )
    train_dataset = forms.FileField(
        label='Training dataset',
        required=False,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'id': 'file_id_train_dataset'
            }
        )
    )
    test_dataset = forms.FileField(
        label='Test dataset',
        required=False,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'id': 'file_id_test_dataset'
            }
        )
    )
    val_dataset = forms.FileField(
        label='Validation dataset',
        required=False,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'id': 'file_id_val_dataset'
            }
        )
    )

    def clean_train_dataset(self):
        cleaned_data = super().clean()
        clean_train_dataset = cleaned_data.get("train_dataset")
        if (not cleaned_data.get("use_url_datasets")) and clean_train_dataset is None:
            raise ValidationError("Training dataset is required")
        return clean_train_dataset

    def clean_test_dataset(self):
        cleaned_data = super().clean()
        clean_test_dataset = cleaned_data.get("test_dataset")
        if (not cleaned_data.get("use_url_datasets")) and clean_test_dataset is None:
            raise ValidationError("Test dataset is required")
        return clean_test_dataset

    def clean_val_dataset(self):
        cleaned_data = super().clean()
        clean_val_dataset = cleaned_data.get("val_dataset")
        if (not cleaned_data.get("use_url_datasets")) and clean_val_dataset is None:
            raise ValidationError("Validation dataset is required")
        return clean_val_dataset


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
