from django import forms
from . import models

class LoginPembeliForm(forms.Form):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={
        "class": "form-control form-control-lg",
        "placeholder": "Masukkan email Anda"
    }))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={
        "class": "form-control form-control-lg",
        "placeholder": "Masukkan password"
    }))


class KeluhanForm(forms.ModelForm):
    # Definisikan Faktur secara manual sebagai ModelChoiceField
    faktur = forms.ModelChoiceField(
        queryset=models.Faktur.objects.none(),  # Defaultnya kosong
        required=False, 
        label="Faktur Terkait",
        empty_label="-- Pilih Faktur (Opsional) --",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = models.Keluhan
        # Hapus 'faktur' dari daftar fields, field lainnya tetap
        fields = ['isi_keluhan', 'foto']
        widgets = {
            'isi_keluhan': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Ambil queryset faktur dari kwargs (dikirim oleh view)
        faktur_queryset = kwargs.pop('faktur_queryset', None) 
        super().__init__(*args, **kwargs)

        # Jika queryset faktur disediakan, set queryset untuk field faktur
        if faktur_queryset is not None:
            self.fields['faktur'].queryset = faktur_queryset


class PembeliRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Masukkan password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ulangi password'
    }))

    class Meta:
        model = models.Pembeli
        fields = ['nama', 'email', 'no_hp', 'alamat', 'kelurahan', 'password']
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama lengkap'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Alamat email'}),
            'no_hp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomor HP'}),
            'alamat': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Alamat lengkap'}),
            'kelurahan': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        if password != confirm:
            raise forms.ValidationError("Password tidak cocok, silakan ulangi.")
        return cleaned_data