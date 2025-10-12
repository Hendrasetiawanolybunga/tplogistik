from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from .models import Barang, Vendor, Pembeli, Faktur, Kecamatan, Kelurahan, Kategori
from .forms import KecamatanForm, KelurahanForm, VendorForm, KategoriForm, BarangForm, PembeliForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

def dashboard_view(request):
    total_barang = Barang.objects.count()
    total_vendor = Vendor.objects.count()
    total_pembeli = Pembeli.objects.count()
    total_faktur = Faktur.objects.count()

    kelurahan_terbanyak = (
        Faktur.objects
        .values('pembeli__kelurahan__nama_kelurahan')
        .annotate(jumlah=Count('id'))
        .order_by('-jumlah')[:5]
    )

    pelanggan_loyal = (
        Faktur.objects
        .values('pembeli__nama')
        .annotate(jumlah=Count('id'))
        .order_by('-jumlah')[:5]
    )

    context = {
        'total_barang': total_barang,
        'total_vendor': total_vendor,
        'total_pembeli': total_pembeli,
        'total_faktur': total_faktur,
        'kelurahan_terbanyak': kelurahan_terbanyak,
        'pelanggan_loyal': pelanggan_loyal,
    }
    return render(request, 'core/dashboard.html', context)



def kecamatan_index(request):
    query = request.GET.get('q', '')
    kecamatan_list = Kecamatan.objects.all()

    if query:
        kecamatan_list = kecamatan_list.filter(
            Q(nama_kecamatan__icontains=query)
        )

    paginator = Paginator(kecamatan_list, 5)  # 5 item per halaman
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'data': page_obj,
        'query': query,
        'current_menu': 'kecamatan',
    }
    return render(request, 'core/kecamatan/index.html', context)


def kecamatan_create(request):
    form = KecamatanForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Data kecamatan berhasil ditambahkan.")
        return redirect('kecamatan_index')
    return render(request, 'core/kecamatan/create.html', {
        'form': form,
        'current_menu': 'kecamatan',
    })

def kecamatan_edit(request, pk):
    kecamatan = get_object_or_404(Kecamatan, pk=pk)
    form = KecamatanForm(request.POST or None, instance=kecamatan)
    if form.is_valid():
        form.save()
        messages.success(request, "Data kecamatan berhasil diperbarui.")
        return redirect('kecamatan_index')
    return render(request, 'core/kecamatan/edit.html', {
        'form': form,
        'kecamatan': kecamatan,
        'current_menu': 'kecamatan',
    })

def kecamatan_delete(request, pk):
    kecamatan = get_object_or_404(Kecamatan, pk=pk)
    kecamatan.delete()
    messages.success(request, "Data kecamatan berhasil dihapus.")
    return redirect('kecamatan_index')





def kelurahan_index(request):
    search_query = request.GET.get('q', '')
    data = Kelurahan.objects.select_related('kecamatan')
    if search_query:
        data = data.filter(nama_kelurahan__icontains=search_query)

    paginator = Paginator(data.order_by('nama_kelurahan'), 5)  # 5 data per halaman
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'current_menu': 'kelurahan',
    }
    return render(request, 'core/kelurahan/index.html', context)

def kelurahan_create(request):
    form = KelurahanForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Data kelurahan berhasil ditambahkan.")
        return redirect('kelurahan_index')
    return render(request, 'core/kelurahan/create.html', {
        'form': form,
        'current_menu': 'kelurahan',
    })

def kelurahan_edit(request, pk):
    kelurahan = get_object_or_404(Kelurahan, pk=pk)
    form = KelurahanForm(request.POST or None, instance=kelurahan)
    if form.is_valid():
        form.save()
        messages.success(request, "Data kelurahan berhasil diperbarui.")
        return redirect('kelurahan_index')
    return render(request, 'core/kelurahan/edit.html', {
        'form': form,
        'kelurahan': kelurahan,
        'current_menu': 'kelurahan',
    })

def kelurahan_delete(request, pk):
    kelurahan = get_object_or_404(Kelurahan, pk=pk)
    kelurahan.delete()
    messages.success(request, "Data kelurahan berhasil dihapus.")
    return redirect('kelurahan_index')




def vendor_index(request):
    vendors = Vendor.objects.all()
    return render(request, 'core/vendor/index.html', {
        'vendors': vendors,
        'current_menu': 'vendor'
    })

def vendor_create(request):
    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vendor_index')
    else:
        form = VendorForm()
    return render(request, 'core/vendor/create.html', {
        'form': form,
        'current_menu': 'vendor'
    })

def vendor_edit(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        form = VendorForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            return redirect('vendor_index')
    else:
        form = VendorForm(instance=vendor)
    return render(request, 'core/vendor/edit.html', {
        'form': form,
        'vendor': vendor,
        'current_menu': 'vendor'
    })

def vendor_delete(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    vendor.delete()
    return redirect('vendor_index')




def kategori_index(request):
    query = request.GET.get('q', '')
    kategori_list = Kategori.objects.filter(nama__icontains=query).order_by('nama')
    return render(request, 'core/kategori/index.html', {
        'page_obj': kategori_list,
        'search_query': query,
        'current_menu': 'kategori',
    })

def kategori_create(request):
    if request.method == 'POST':
        form = KategoriForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kategori berhasil ditambahkan.')
            return redirect('kategori_index')
    else:
        form = KategoriForm()
    return render(request, 'core/kategori/create.html', {
        'form': form,
        'current_menu': 'kategori',
    })

def kategori_edit(request, pk):
    kategori = get_object_or_404(Kategori, pk=pk)
    if request.method == 'POST':
        form = KategoriForm(request.POST, instance=kategori)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kategori berhasil diperbarui.')
            return redirect('kategori_index')
    else:
        form = KategoriForm(instance=kategori)
    return render(request, 'core/kategori/edit.html', {
        'form': form,
        'current_menu': 'kategori',
    })

def kategori_delete(request, pk):
    kategori = get_object_or_404(Kategori, pk=pk)
    kategori.delete()
    messages.success(request, 'Kategori berhasil dihapus.')
    return redirect('kategori_index')



def barang_index(request):
    search_query = request.GET.get('q', '')
    barang_list = Barang.objects.all()

    if search_query:
        barang_list = barang_list.filter(
            Q(nama_barang__icontains=search_query) |
            Q(kategori__nama__icontains=search_query)
        )

    paginator = Paginator(barang_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/barang/index.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'current_menu': 'barang',
    })

def barang_create(request):
    if request.method == 'POST':
        form = BarangForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Barang berhasil ditambahkan.')
            return redirect('barang_index')
    else:
        form = BarangForm()

    return render(request, 'core/barang/create.html', {
        'form': form,
        'current_menu': 'barang',
    })

def barang_edit(request, pk):
    barang = get_object_or_404(Barang, pk=pk)
    if request.method == 'POST':
        form = BarangForm(request.POST, instance=barang)
        if form.is_valid():
            form.save()
            messages.success(request, 'Barang berhasil diperbarui.')
            return redirect('barang_index')
    else:
        form = BarangForm(instance=barang)

    return render(request, 'core/barang/edit.html', {
        'form': form,
        'barang': barang,
        'current_menu': 'barang',
    })

def barang_delete(request, pk):
    barang = get_object_or_404(Barang, pk=pk)
    barang.delete()
    messages.success(request, 'Barang berhasil dihapus.')
    return redirect('barang_index')



def pembeli_index(request):
    search_query = request.GET.get('q', '')
    pembeli_list = Pembeli.objects.filter(
        Q(nama__icontains=search_query) |
        Q(no_hp__icontains=search_query)
    ).order_by('nama')

    paginator = Paginator(pembeli_list, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'current_menu': 'pembeli'
    }
    return render(request, 'core/pembeli/index.html', context)

def pembeli_create(request):
    if request.method == 'POST':
        form = PembeliForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data pembeli berhasil ditambahkan.')
            return redirect('pembeli_index')
    else:
        form = PembeliForm()

    context = {
        'form': form,
        'current_menu': 'pembeli'
    }
    return render(request, 'core/pembeli/create.html', context)

def pembeli_edit(request, pk):
    pembeli = get_object_or_404(Pembeli, pk=pk)
    if request.method == 'POST':
        form = PembeliForm(request.POST, instance=pembeli)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data pembeli berhasil diperbarui.')
            return redirect('pembeli_index')
    else:
        form = PembeliForm(instance=pembeli)

    context = {
        'form': form,
        'current_menu': 'pembeli'
    }
    return render(request, 'core/pembeli/edit.html', context)

def pembeli_delete(request, pk):
    pembeli = get_object_or_404(Pembeli, pk=pk)
    pembeli.delete()
    messages.success(request, 'Data pembeli berhasil dihapus.')
    return redirect('pembeli_index')