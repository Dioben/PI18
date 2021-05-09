from django import forms


class UploadModelFileForm(forms.Form):
    #title = forms.CharField(max_length=50)
    model = forms.FileField(label='Select a Model')

class UploadDataSetFileForm(forms.Form):
    #title = forms.CharField(max_length=50)
    dataset = forms.FileField(label='Select a DataSet')