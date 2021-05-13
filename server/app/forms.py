from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator


class UploadModelFileForm(forms.Form):
    #title = forms.CharField(max_length=50)
    model = forms.FileField(label='Select a Model')

class UploadDataSetFileForm(forms.Form):
    #title = forms.CharField(max_length=50)
    dataset = forms.FileField(label='Select a DataSet')

class ConfSimForm(forms.Form):
    name = forms.CharField(max_length=100)
    max_epochs = forms.IntegerField(validators=[MinValueValidator(1)])
    logging_interval = forms.IntegerField(validators=[MinValueValidator(1)])

    def clean_logging_interval(self):
        if self.logging_interval> self.max_epochs:
            raise ValidationError("Logging interval is larger than total runtime")