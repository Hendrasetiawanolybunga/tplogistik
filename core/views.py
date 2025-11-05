from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth.hashers import make_password, check_password
from . import models
from .forms import LoginPembeliForm, KeluhanForm, PembeliRegisterForm
from functools import wraps

# Helper decorators
def pembeli_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'pembeli_id' not in request.session:
            return redirect('pembeli_login')
        return view_func(request, *args, **kwargs)
    return wrapper

def vendor_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'vendor_id' not in request.session:
            return redirect('vendor_login')
        return view_func(request, *args, **kwargs)
    return wrapper

def index(request):
    return render(request, 'index.html')

# Pembeli Views
def pembeli_register(request):
    if request.method == 'POST':
        form = PembeliRegisterForm(request.POST)
        if form.is_valid():
            pembeli = form.save(commit=False)
            # Use make_password to hash the password before saving
            pembeli.password = make_password(form.cleaned_data['password'])
            pembeli.save()
            messages.success(request, "Registrasi berhasil! Silakan login menggunakan akun Anda.")
            return redirect('pembeli_login')
    else:
        form = PembeliRegisterForm()

    return render(request, 'pembeli/pembeli_register.html', {'form': form})

def pembeli_login(request):
    if request.method == 'POST':
        form = LoginPembeliForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                pembeli = models.Pembeli.objects.get(email=email)
                # Use check_password to verify the password
                if check_password(password, pembeli.password):
                    request.session['pembeli_id'] = pembeli.id_pembeli
                    request.session['pembeli_nama'] = pembeli.nama
                    messages.success(request, f"Selamat datang, {pembeli.nama}!")
                    return redirect('pembeli_dashboard')
                else:
                    messages.error(request, "Email atau password salah!")
            except models.Pembeli.DoesNotExist:
                messages.error(request, "Email atau password salah!")
    else:
        form = LoginPembeliForm()

    return render(request, 'pembeli/pembeli_login.html', {'form': form})

def pembeli_logout(request):
    request.session.flush()
    messages.success(request, "Anda telah logout.")
    return redirect('pembeli_login')

@pembeli_required
def pembeli_dashboard(request):
    pembeli_id = request.session.get('pembeli_id')
    pembeli = models.Pembeli.objects.get(pk=pembeli_id)
    faktur_list = models.Faktur.objects.filter(pembeli=pembeli).order_by('-id_faktur')[:5]  # Last 5 invoices

    return render(request, 'pembeli/pembeli_dashboard.html', {
        'pembeli': pembeli,
        'faktur_list': faktur_list
    })

@pembeli_required
def pembeli_keluhan_buat(request):
    pembeli_id = request.session.get('pembeli_id')
    pembeli = models.Pembeli.objects.get(pk=pembeli_id)
    
    # Filter Faktur hanya untuk Pembeli yang sedang login
    faktur_pembeli = models.Faktur.objects.filter(pembeli=pembeli)
    
    if request.method == 'POST':
        # Instantiate Form dengan queryset yang sudah difilter
        form = KeluhanForm(request.POST, request.FILES, faktur_queryset=faktur_pembeli)
        if form.is_valid():
            keluhan = form.save(commit=False)
            keluhan.pembeli = pembeli

            # Logika KRITIS: Ambil ID dari objek Faktur yang dipilih dan simpan sebagai string
            faktur_obj = form.cleaned_data.get('faktur')
            if faktur_obj:
                keluhan.faktur = str(faktur_obj.id_faktur)  # Menyimpan ID Faktur sebagai string
            else:
                keluhan.faktur = None  # Jika tidak ada faktur yang dipilih

            # Simpan objek keluhan yang sudah dimodifikasi
            keluhan.save()
            messages.success(request, "Keluhan Anda berhasil dikirim.")
            return redirect('pembeli_dashboard')
    else:
        # Instantiate Form dengan queryset yang sudah difilter
        form = KeluhanForm(faktur_queryset=faktur_pembeli)

    return render(request, 'pembeli/pembeli_keluhan_buat.html', {'form': form})

@pembeli_required
def pembeli_keluhan_riwayat(request):
    pembeli_id = request.session.get('pembeli_id')
    pembeli = models.Pembeli.objects.get(pk=pembeli_id)
    keluhan_list = models.Keluhan.objects.filter(pembeli=pembeli).order_by('-tanggal')

    return render(request, 'pembeli/pembeli_keluhan_riwayat.html', {
        'pembeli': pembeli,
        'keluhan_list': keluhan_list
    })

# Vendor Views
def vendor_register(request):
    if request.method == 'POST':
        nama = request.POST.get('nama')
        email = request.POST.get('email')
        no_hp = request.POST.get('no_hp')
        alamat = request.POST.get('alamat')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Basic validation
        if not all([nama, email, no_hp, alamat, password]):
            messages.error(request, "Semua field harus diisi!")
            return render(request, 'vendor/vendor_register.html')
        
        if password != confirm_password:
            messages.error(request, "Password tidak cocok!")
            return render(request, 'vendor/vendor_register.html')
        
        # Check if vendor with this email already exists
        if models.Vendor.objects.filter(email=email).exists():
            messages.error(request, "Email sudah terdaftar!")
            return render(request, 'vendor/vendor_register.html')
        
        # Create vendor with hashed password
        vendor = models.Vendor(
            nama=nama,
            email=email,
            no_hp=no_hp,
            alamat=alamat
        )
        # Hash the password before saving
        vendor.password = make_password(password)
        vendor.save()
        
        messages.success(request, "Registrasi vendor berhasil! Silakan login.")
        return redirect('vendor_login')
    
    return render(request, 'vendor/vendor_register.html')

def vendor_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Use filter().first() instead of get() to handle potential non-unique emails
        vendor = models.Vendor.objects.filter(email=email).first()
        if vendor is None:
            messages.error(request, "Email atau password salah!")
        # Use check_password to verify the password
        elif check_password(password, vendor.password):
            request.session['vendor_id'] = vendor.id_vendor
            request.session['vendor_nama'] = vendor.nama
            messages.success(request, f"Selamat datang, {vendor.nama}!")
            return redirect('vendor_dashboard')
        else:
            messages.error(request, "Email atau password salah!")
    return render(request, 'vendor/vendor_login.html')

def vendor_logout(request):
    request.session.flush()
    messages.success(request, "Anda telah logout.")
    return redirect('vendor_login')

@vendor_required
def vendor_dashboard(request):
    vendor_id = request.session.get('vendor_id')
    vendor = models.Vendor.objects.get(pk=vendor_id)

    return render(request, 'vendor/vendor_dashboard.html', {
        'vendor': vendor
    })

@vendor_required
def vendor_keluhan_laporan(request):
    vendor_id = request.session.get('vendor_id')
    vendor = models.Vendor.objects.get(pk=vendor_id)
    
    # Get keluhan related to this vendor's faktur
    keluhan_list = models.Keluhan.objects.filter(
        pembeli__faktur__vendor=vendor
    ).distinct().order_by('-tanggal')

    return render(request, 'vendor/vendor_keluhan_laporan.html', {
        'vendor': vendor,
        'keluhan_list': keluhan_list
    })