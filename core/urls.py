from django.urls import path
from .views import dashboard_view
from . import views

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    # Kecamatan URLs
    path('kecamatan/', views.kecamatan_index, name='kecamatan_index'),
    path('kecamatan/tambah/', views.kecamatan_create, name='kecamatan_create'),
    path('kecamatan/edit/<int:pk>/', views.kecamatan_edit, name='kecamatan_edit'),
    path('kecamatan/hapus/<int:pk>/', views.kecamatan_delete, name='kecamatan_delete'),
    # kelurahan URLs
    path('kelurahan/', views.kelurahan_index, name='kelurahan_index'),
    path('kelurahan/tambah/', views.kelurahan_create, name='kelurahan_create'),
    path('kelurahan/edit/<int:pk>/', views.kelurahan_edit, name='kelurahan_edit'),
    path('kelurahan/hapus/<int:pk>/', views.kelurahan_delete, name='kelurahan_delete'),
    # Vendor URLs
    path('vendor/', views.vendor_index, name='vendor_index'),
    path('vendor/create/', views.vendor_create, name='vendor_create'),
    path('vendor/edit/<int:pk>/', views.vendor_edit, name='vendor_edit'),
    path('vendor/delete/<int:pk>/', views.vendor_delete, name='vendor_delete'),
    # Kategori URLs
    path('kategori/', views.kategori_index, name='kategori_index'),
    path('kategori/create/', views.kategori_create, name='kategori_create'),
    path('kategori/edit/<int:pk>/', views.kategori_edit, name='kategori_edit'),
    path('kategori/delete/<int:pk>/', views.kategori_delete, name='kategori_delete'),
    # Barang URLs
    path('barang/', views.barang_index, name='barang_index'),
    path('barang/create/', views.barang_create, name='barang_create'),
    path('barang/edit/<int:pk>/', views.barang_edit, name='barang_edit'),
    path('barang/delete/<int:pk>/', views.barang_delete, name='barang_delete'),
    # Pembeli URLs
    path('pembeli/', views.pembeli_index, name='pembeli_index'),
    path('pembeli/create/', views.pembeli_create, name='pembeli_create'),
    path('pembeli/edit/<int:pk>/', views.pembeli_edit, name='pembeli_edit'),
    path('pembeli/delete/<int:pk>/', views.pembeli_delete, name='pembeli_delete'),
]
