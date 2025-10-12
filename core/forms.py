from django import forms
from .models import Kecamatan, Kelurahan, Vendor, Kategori, Barang, Pembeli

class KecamatanForm(forms.ModelForm):
    class Meta:
        model = Kecamatan
        fields = ['nama_kecamatan']
        widgets = {
            'nama_kecamatan': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan nama kecamatan...'
            })
        }

class KelurahanForm(forms.ModelForm):
    class Meta:
        model = Kelurahan
        fields = ['nama_kelurahan', 'kode_pos', 'kecamatan']
        widgets = {
            'nama_kelurahan': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan nama kecamatan...'
            }),
            'kode_pos': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan kode pos...'
            })
        }
        

class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['nama', 'email', 'alamat', 'no_hp']
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Vendor'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'alamat': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Alamat'}),
            'no_hp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomor HP'}),
        }
        
        
class KategoriForm(forms.ModelForm):
    class Meta:
        model = Kategori
        fields = ['nama']
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama kategori'}),
        }
        

class BarangForm(forms.ModelForm):
    class Meta:
        model = Barang
        fields = ['nama_barang', 'harga_barang', 'kategori']
        widgets = {
            'nama_barang': forms.TextInput(attrs={'class': 'form-control'}),
            'harga_barang': forms.NumberInput(attrs={'class': 'form-control'}),
            'kategori': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'nama_barang': 'Nama Barang',
            'harga_barang': 'Harga Barang',
            'kategori': 'Kategori',
        }
        
class PembeliForm(forms.ModelForm):
    class Meta:
        model = Pembeli
        fields = ['nama', 'alamat', 'no_hp', 'kelurahan']
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control'}),
            'alamat': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'no_hp': forms.TextInput(attrs={'class': 'form-control'}),
            'kelurahan': forms.Select(attrs={'class': 'form-control'}),
        }