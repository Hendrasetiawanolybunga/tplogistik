from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST
from .models import Kurir, Faktur, DetailFaktur


# ========== LOGIN KURIR ==========
def kurir_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            kurir = Kurir.objects.get(email=email, password=password)
            if not kurir.aktif:
                messages.error(request, "Akun Anda tidak aktif.")
                return redirect("kurir_login")

            # Simpan sesi login kurir
            request.session["kurir_id"] = kurir.id_kurir
            request.session["kurir_nama"] = kurir.nama
            return redirect("kurir_dashboard")
        except Kurir.DoesNotExist:
            messages.error(request, "Email atau password salah.")
    return render(request, "core/kurir/login.html")


# ========== DASHBOARD KURIR ==========
def kurir_dashboard(request):
    kurir_id = request.session.get("kurir_id")
    if not kurir_id:
        return redirect("kurir_login")

    faktur_list = Faktur.objects.filter(kurir_id=kurir_id).select_related("pembeli", "vendor")

    return render(request, "core/kurir/dashboard.html", {
        "faktur_list": faktur_list,
        "kurir_nama": request.session.get("kurir_nama")
    })


# ========== DETAIL FAKTUR ==========
def kurir_faktur_detail(request, faktur_id):
    kurir_id = request.session.get("kurir_id")
    if not kurir_id:
        return redirect("kurir_login")

    faktur = get_object_or_404(Faktur, id_faktur=faktur_id)

    # Cegah akses faktur milik kurir lain
    if faktur.kurir_id != kurir_id:
        return HttpResponseForbidden("Anda tidak berhak melihat faktur ini.")

    detail_list = DetailFaktur.objects.filter(faktur=faktur).select_related("barang")

    return render(request, "core/kurir/faktur_detail.html", {
        "faktur": faktur,
        "detail_list": detail_list,
        "kurir_nama": request.session.get("kurir_nama")
    })


# ========== UPDATE STATUS + FOTO PENGIRIMAN ==========
@require_POST
def kurir_update_status(request, faktur_id):
    kurir_id = request.session.get("kurir_id")
    if not kurir_id:
        return redirect("kurir_login")

    faktur = get_object_or_404(Faktur, id_faktur=faktur_id)

    # Pastikan kurir hanya bisa ubah faktur miliknya
    if faktur.kurir_id != kurir_id:
        return HttpResponseForbidden("Anda tidak boleh mengubah faktur milik kurir lain.")

    new_status = request.POST.get("status")
    foto_pengiriman = request.FILES.get("foto_pengiriman")

    # Validasi status
    if new_status in dict(Faktur.STATUS_CHOICES):
        faktur.status = new_status

        # Simpan foto jika diupload
        if foto_pengiriman:
            faktur.foto_pengiriman = foto_pengiriman

        faktur.save()
        messages.success(request, f"Status faktur #{faktur.id_faktur} diperbarui menjadi '{new_status}'.")
    else:
        messages.error(request, "Status tidak valid.")

    return redirect("kurir_faktur_detail", faktur_id=faktur.id_faktur)


# ========== LOGOUT ==========
def kurir_logout(request):
    logout(request)
    request.session.flush()
    return redirect("kurir_login")
