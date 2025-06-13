from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Pagamento

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)

class PagamentoForm(forms.ModelForm):
    class Meta:
        model = Pagamento
        fields = ['credor', 'contrato', 'valor', 'data', 'periodo', 'fatura', 'nota_fiscal']
        widgets = {
            'data': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'credor': forms.Select(attrs={'class': 'form-control'}),
            'contrato': forms.Select(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control'}),
            'periodo': forms.TextInput(attrs={'class': 'form-control'}),
            'fatura': forms.TextInput(attrs={'class': 'form-control'}),
            'nota_fiscal': forms.TextInput(attrs={'class': 'form-control'}),
        }