from django.urls import path
from . import views_kurir
from . import views

urlpatterns = [
    path("", views.index, name="beranda"),
    path("kurir/login/", views_kurir.kurir_login, name="kurir_login"),
    path("kurir/dashboard/", views_kurir.kurir_dashboard, name="kurir_dashboard"),
    path("kurir/faktur/<int:faktur_id>/", views_kurir.kurir_faktur_detail, name="kurir_faktur_detail"),
    path("kurir/logout/", views_kurir.kurir_logout, name="kurir_logout"),
    path("kurir/faktur/<int:faktur_id>/update-status/", views_kurir.kurir_update_status, name="kurir_update_status"),
    
    # Pembeli URLs
    path("pembeli/register/", views.pembeli_register, name="pembeli_register"),
    path("pembeli/login/", views.pembeli_login, name="pembeli_login"),
    path("pembeli/logout/", views.pembeli_logout, name="pembeli_logout"),
    path("pembeli/dashboard/", views.pembeli_dashboard, name="pembeli_dashboard"),
    path("pembeli/keluhan/buat/", views.pembeli_keluhan_buat, name="pembeli_keluhan_buat"),
    path("pembeli/keluhan/riwayat/", views.pembeli_keluhan_riwayat, name="pembeli_keluhan_riwayat"),
    
    # Vendor URLs
    path("vendor/register/", views.vendor_register, name="vendor_register"),
    path("vendor/login/", views.vendor_login, name="vendor_login"),
    path("vendor/logout/", views.vendor_logout, name="vendor_logout"),
    path("vendor/dashboard/", views.vendor_dashboard, name="vendor_dashboard"),
    path("vendor/keluhan/laporan/", views.vendor_keluhan_laporan, name="vendor_keluhan_laporan"),
]