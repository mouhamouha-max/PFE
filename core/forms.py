from django import forms

class PacketFilterForm(forms.Form):
    from_value = forms.CharField(label='From', max_length=100, required=False)
    to_value = forms.CharField(label='To', max_length=100, required=False)
