from django.contrib import admin
from .models import Kecamatan, Kelurahan, Pembeli, Vendor, Kategori, Barang, Kurir, Faktur, DetailFaktur, Keluhan
from django.contrib.auth.models import Group

admin.site.unregister(Group)
from django.contrib.admin import AdminSite
from django.urls import path
from django.template.response import TemplateResponse
from core.models import Vendor, Pembeli, Barang, Faktur

class MyAdminSite(AdminSite):
    site_header = 'Admin Dashboard'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view))
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        context = dict(
            self.each_context(request),
            vendor_count=Vendor.objects.count(),
            pembeli_count=Pembeli.objects.count(),
            barang_count=Barang.objects.count(),
            faktur_count=Faktur.objects.count(),
        )
        return TemplateResponse(request, "admin/dashboard.html", context)

admin_site = MyAdminSite(name='myadmin')

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

@admin.register(Faktur)
class FakturAdmin(admin.ModelAdmin):
    list_display = ('id_faktur', 'pembeli', 'vendor', 'kurir', 'status', 'total_faktur', 'berat', 'koli')
    list_filter = ('status', 'kurir', 'vendor')
    search_fields = ('id_faktur', 'pembeli__nama', 'vendor__nama', 'kurir__nama')
    inlines = [DetailFakturInline]
    autocomplete_fields = ['pembeli', 'vendor', 'kurir']

@admin.register(Keluhan)
class KeluhanAdmin(admin.ModelAdmin):
    list_display = ('id_keluhan', 'pembeli', 'isi_keluhan', 'foto_keluhan')
    list_filter = ('pembeli',)
    search_fields = ('pembeli__nama', 'isi_keluhan')
    autocomplete_fields = ['pembeli']