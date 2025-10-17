from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import path
from django.shortcuts import redirect
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum, F
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .models import (
    Kecamatan, Kelurahan, Pembeli, Vendor, Kategori, Barang, Kurir,
    Faktur, DetailFaktur, Keluhan
)

# ========== PENDAFTARAN MODEL BIASA ==========
@admin.register(Kecamatan)
class KecamatanAdmin(admin.ModelAdmin):
    list_display = ('id_kecamatan', 'nama_kecamatan')
    search_fields = ('nama_kecamatan',)


@admin.register(Kelurahan)
class KelurahanAdmin(admin.ModelAdmin):
    list_display = ('id_kelurahan', 'nama_kelurahan', 'kode_pos', 'kecamatan')
    list_filter = ('kecamatan',)
    search_fields = ('nama_kelurahan', 'kode_pos')


@admin.register(Pembeli)
class PembeliAdmin(admin.ModelAdmin):
    list_display = ('id_pembeli', 'nama', 'no_hp', 'kelurahan')
    list_filter = ('kelurahan',)
    search_fields = ('nama', 'no_hp', 'alamat')


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('id_vendor', 'nama', 'email', 'no_hp')
    search_fields = ('nama', 'email', 'no_hp')


@admin.register(Kategori)
class KategoriAdmin(admin.ModelAdmin):
    list_display = ('id_kategori', 'nama')
    search_fields = ('nama',)


@admin.register(Barang)
class BarangAdmin(admin.ModelAdmin):
    list_display = ('id_barang', 'nama_barang', 'harga_barang', 'kategori')
    list_filter = ('kategori',)
    search_fields = ('nama_barang',)


@admin.register(Kurir)
class KurirAdmin(admin.ModelAdmin):
    list_display = ('id_kurir', 'nama_kurir', 'no_hp')
    search_fields = ('nama_kurir', 'no_hp')


class DetailFakturInline(admin.TabularInline):
    model = DetailFaktur
    extra = 1
    autocomplete_fields = ['barang']


# ========== PENYESUAIAN UNTUK PERAN KURIR ==========
@admin.register(Faktur)
class FakturAdmin(admin.ModelAdmin):
    list_display = ('id_faktur', 'pembeli', 'vendor', 'kurir', 'status', 'total_faktur', 'berat', 'koli')
    list_filter = ('status', 'kurir', 'vendor')
    search_fields = ('id_faktur', 'pembeli__nama', 'vendor__nama', 'kurir__nama')
    inlines = [DetailFakturInline]
    autocomplete_fields = ['pembeli', 'vendor', 'kurir']

    # Hanya field tertentu yang bisa diedit oleh Kurir
    def get_readonly_fields(self, request, obj=None):
        if request.user.groups.filter(name='Kurir').exists():
            return [f.name for f in self.model._meta.fields if f.name not in ('foto_pengiriman', 'status')]
        return super().get_readonly_fields(request, obj)

    # Batasi queryset agar Kurir hanya bisa melihat faktur yang ditugaskan padanya
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='Kurir').exists():
            return qs.filter(kurir__nama_kurir=request.user.get_full_name())
        return qs

    def has_add_permission(self, request):
        # Kurir dan Pimpinan tidak boleh menambah faktur
        if request.user.groups.filter(name__in=['Kurir', 'Pimpinan']).exists():
            return False
        return True  # Admin / Superuser boleh

    def has_delete_permission(self, request, obj=None):
        if request.user.groups.filter(name='Kurir').exists():
            return False
        return True


@admin.register(Keluhan)
class KeluhanAdmin(admin.ModelAdmin):
    list_display = ('id_keluhan', 'pembeli', 'isi_keluhan', 'foto_keluhan')
    list_filter = ('pembeli',)
    search_fields = ('pembeli__nama', 'isi_keluhan')
    autocomplete_fields = ['pembeli']


# ========== ADMIN SITE KUSTOM UNTUK ROLE-BASED DASHBOARD ==========
class MyAdminSite(AdminSite):
    site_header = "Dashboard Sistem Pengiriman"
    site_title = "Manajemen Pengiriman"
    index_title = "Selamat Datang di Sistem Admin"

    def index(self, request, extra_context=None):
        """
        Override halaman utama (index) untuk mengarahkan pengguna
        sesuai dengan peran (Group) yang dimiliki tanpa template kustom.
        """
        user = request.user

        # Superuser atau Admin masuk ke halaman dashboard bawaan
        if user.is_superuser or user.groups.filter(name='Admin').exists():
            return super().index(request, extra_context)

        # Kurir diarahkan langsung ke daftar Faktur
        elif user.groups.filter(name='Kurir').exists():
            return redirect('/admin/core/faktur/')

        # Pimpinan diarahkan ke tampilan laporan
        elif user.groups.filter(name='Pimpinan').exists():
            return redirect('admin:laporan_faktur_detail')

        # Jika tidak punya group sama sekali
        return super().index(request, extra_context)

    def get_urls(self):
        """
        Tambahkan URL kustom untuk laporan pimpinan (tanpa template).
        """
        urls = super().get_urls()
        custom_urls = [
            path('laporan_faktur_detail/', self.admin_view(self.laporan_faktur_detail), name='laporan_faktur_detail'),
            path('laporan_faktur_pdf/', self.admin_view(self.export_pdf), name='laporan_faktur_pdf'),
        ]
        return custom_urls + urls

    @user_passes_test(lambda u: u.groups.filter(name='Pimpinan').exists() or u.is_superuser)
    def laporan_faktur_detail(self, request):
        """
        View sederhana (tanpa template) untuk menampilkan data gabungan Faktur + DetailFaktur.
        Ditampilkan sebagai halaman HTML bawaan (plain).
        """
        faktur_data = (
            DetailFaktur.objects
            .select_related('faktur', 'barang')
            .annotate(
                pembeli_nama=F('faktur__pembeli__nama'),
                vendor_nama=F('faktur__vendor__nama'),
                kurir_nama=F('faktur__kurir__nama_kurir'),
                status=F('faktur__status'),
                total_faktur=F('faktur__total_faktur')
            )
        )

        html = "<h1>Laporan Faktur dan Detail Faktur</h1>"
        html += "<p><a href='/admin/laporan_faktur_pdf/'>Unduh PDF</a></p>"
        html += "<table border='1' cellpadding='5'><tr><th>ID Faktur</th><th>Pembeli</th><th>Vendor</th><th>Barang</th><th>Jumlah</th><th>Status</th><th>Total</th></tr>"

        for d in faktur_data:
            html += f"<tr><td>{d.faktur.id_faktur}</td><td>{d.pembeli_nama}</td><td>{d.vendor_nama}</td><td>{d.barang.nama_barang}</td><td>{d.jumlah_barang}</td><td>{d.status}</td><td>{d.total_faktur}</td></tr>"

        html += "</table>"
        return HttpResponse(html)

    @user_passes_test(lambda u: u.groups.filter(name='Pimpinan').exists() or u.is_superuser)
    def export_pdf(self, request):
        """
        Membuat laporan PDF menggunakan ReportLab tanpa template tambahan.
        """
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="laporan_faktur.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4
        y = height - 50

        p.setFont("Helvetica-Bold", 14)
        p.drawString(200, y, "Laporan Faktur dan Detail Faktur")
        y -= 30
        p.setFont("Helvetica", 10)

        data = (
            DetailFaktur.objects
            .select_related('faktur', 'barang', 'faktur__pembeli', 'faktur__vendor')
        )

        for item in data:
            line = f"Faktur #{item.faktur.id_faktur} | Pembeli: {item.faktur.pembeli.nama} | Vendor: {item.faktur.vendor.nama} | Barang: {item.barang.nama_barang} | Jumlah: {item.jumlah_barang} | Status: {item.faktur.status}"
            p.drawString(30, y, line)
            y -= 15
            if y < 50:
                p.showPage()
                p.setFont("Helvetica", 10)
                y = height - 50

        p.save()
        return response


# Inisialisasi AdminSite kustom
admin_site = MyAdminSite(name='myadmin')
