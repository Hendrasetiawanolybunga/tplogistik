from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Pembeli, Keluhan
from .forms import LoginPembeliForm, KeluhanForm, PembeliRegisterForm


def index(request):
    return render(request, 'core/dashboard.html')
def pembeli_login(request):
    if request.method == 'POST':
        form = LoginPembeliForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                pembeli = Pembeli.objects.get(email=email, password=password)
                request.session['pembeli_id'] = pembeli.id_pembeli
                request.session['pembeli_nama'] = pembeli.nama
                messages.success(request, f"Selamat datang, {pembeli.nama}!")
                return redirect('pembeli_dashboard')
            except Pembeli.DoesNotExist:
                messages.error(request, "Email atau password salah!")
    else:
        form = LoginPembeliForm()

    return render(request, 'core/login.html', {'form': form})


def pembeli_logout(request):
    request.session.flush()
    messages.success(request, "Anda telah logout.")
    return redirect('pembeli_login')


def pembeli_dashboard(request):
    pembeli_id = request.session.get('pembeli_id')
    if not pembeli_id:
        return redirect('pembeli_login')

    pembeli = Pembeli.objects.get(pk=pembeli_id)
    keluhan_list = Keluhan.objects.filter(pembeli=pembeli).order_by('-tanggal')

    return render(request, 'core/pembeli_dashboard.html', {
        'pembeli': pembeli,
        'keluhan_list': keluhan_list
    })


def kirim_keluhan(request):
    pembeli_id = request.session.get('pembeli_id')
    if not pembeli_id:
        return redirect('pembeli_login')

    pembeli = Pembeli.objects.get(pk=pembeli_id)

    if request.method == 'POST':
        form = KeluhanForm(request.POST, request.FILES)
        if form.is_valid():
            keluhan = form.save(commit=False)
            keluhan.pembeli = pembeli
            keluhan.save()
            messages.success(request, "Keluhan Anda berhasil dikirim.")
            return redirect('pembeli_dashboard')
    else:
        form = KeluhanForm()

    return render(request, 'core/kirim_keluhan.html', {'form': form})




def register_pembeli(request):
    if request.method == 'POST':
        form = PembeliRegisterForm(request.POST)
        if form.is_valid():
            pembeli = form.save(commit=False)
            pembeli.set_password(form.cleaned_data['password'])
            pembeli.save()
            messages.success(request, "Registrasi berhasil! Silakan login menggunakan akun Anda.")
            return redirect('pembeli_login')
    else:
        form = PembeliRegisterForm()

    return render(request, 'core/register_pembeli.html', {'form': form})
