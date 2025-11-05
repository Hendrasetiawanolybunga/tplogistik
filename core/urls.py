from django.urls import path
from . import views_kurir

urlpatterns = [
    path("kurir/login/", views_kurir.kurir_login, name="kurir_login"),
    path("kurir/dashboard/", views_kurir.kurir_dashboard, name="kurir_dashboard"),
    path("kurir/faktur/<int:faktur_id>/", views_kurir.kurir_faktur_detail, name="kurir_faktur_detail"),
    path("kurir/logout/", views_kurir.kurir_logout, name="kurir_logout"),
    path("kurir/faktur/<int:faktur_id>/update-status/", views_kurir.kurir_update_status, name="kurir_update_status"),

]
