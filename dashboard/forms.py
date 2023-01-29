from django import forms


class UploadPictureToAnalyze(forms.Form):
    file = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True, 'class': 'form-control', 'id': 'file'}))
