# core/admin.py
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import path
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Count
from django.http import HttpResponse

# 🔹 ReportLab untuk PDF profesional
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)

from .models import (
    Kecamatan, Kelurahan, Pembeli, Vendor, Kategori, Barang,
    Faktur, DetailFaktur, Keluhan
)

User = get_user_model()


# =================== KECAMATAN ===================
@admin.register(Kecamatan)
class KecamatanAdmin(admin.ModelAdmin):
    list_display = ('id_kecamatan', 'nama_kecamatan')
    search_fields = ('nama_kecamatan',)


# =================== KELURAHAN ===================
@admin.register(Kelurahan)
class KelurahanAdmin(admin.ModelAdmin):
    list_display = ('id_kelurahan', 'nama_kelurahan', 'kode_pos', 'kecamatan')
    list_filter = ('kecamatan',)
    search_fields = ('nama_kelurahan', 'kode_pos')
    actions = ["export_kelurahan_terbanyak"]

    def export_kelurahan_terbanyak(self, request, queryset):
        """Cetak laporan kelurahan paling sering dikirim"""
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=laporan_kelurahan.pdf"

        doc = SimpleDocTemplate(response, pagesize=A4,
                                leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=60)
        styles = getSampleStyleSheet()
        elements = []

        # Judul
        title_style = ParagraphStyle(
            name="Title",
            fontSize=16,
            alignment=1,
            spaceAfter=20,
            leading=20,
        )
        elements.append(Paragraph("LAPORAN DATA KELURAHAN TRIO PRIMA LOGISTIK", title_style))
        elements.append(Spacer(1, 12))

        # Ambil data
        data = (
            Kelurahan.objects
            .annotate(total_pengiriman=Count("pembeli__faktur"))
            .filter(total_pengiriman__gt=0)
            .order_by("-total_pengiriman")
        )

        # Header tabel
        table_data = [["No", "Nama Kelurahan", "Kecamatan", "Kode Pos", "Total Pengiriman"]]
        for i, k in enumerate(data, start=1):
            table_data.append([
                str(i),
                k.nama_kelurahan,
                k.kecamatan.nama_kecamatan,
                k.kode_pos,
                str(k.total_pengiriman)
            ])

        # Tabel
        table = Table(table_data, repeatRows=1, colWidths=[30, 120, 120, 80, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#203864")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
        ]))
        elements.append(table)

        # Tanda tangan
        elements.append(Spacer(1, 30))
        elements.append(Paragraph(
            "Mengetahui,",
            ParagraphStyle(name="left", alignment=2, fontSize=11)
        ))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(
            "<b>Pimpinan Trio Prima Logistik</b>", 
            ParagraphStyle(name="center", alignment=2, fontSize=11)
        ))
        elements.append(Spacer(1, 40))
        elements.append(Paragraph("................................................", ParagraphStyle(name="center", alignment=2)))

        doc.build(elements)
        return response

    export_kelurahan_terbanyak.short_description = "Cetak Laporan Kelurahan (PDF)"


# =================== PEMBELI ===================
@admin.register(Pembeli)
class PembeliAdmin(admin.ModelAdmin):
    list_display = ('id_pembeli', 'nama', 'no_hp', 'kelurahan')
    list_filter = ('kelurahan',)
    search_fields = ('nama', 'no_hp', 'alamat')


# =================== VENDOR ===================
@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('id_vendor', 'nama', 'email', 'no_hp')
    search_fields = ('nama', 'email', 'no_hp')


# =================== KATEGORI ===================
@admin.register(Kategori)
class KategoriAdmin(admin.ModelAdmin):
    list_display = ('id_kategori', 'nama')
    search_fields = ('nama',)


# =================== BARANG ===================
@admin.register(Barang)
class BarangAdmin(admin.ModelAdmin):
    list_display = ('id_barang', 'nama_barang', 'harga_barang', 'kategori')
    list_filter = ('kategori',)
    search_fields = ('nama_barang',)


# =================== DETAIL FAKTUR INLINE ===================
class DetailFakturInline(admin.TabularInline):
    model = DetailFaktur
    extra = 1
    autocomplete_fields = ['barang']


# =================== FAKTUR ===================
@admin.register(Faktur)
class FakturAdmin(admin.ModelAdmin):
    list_display = ('id_faktur', 'pembeli', 'vendor', 'get_kurir_display', 'status', 'total_faktur', 'berat', 'koli')
    list_filter = ('status', 'vendor', 'kurir__username')
    search_fields = ('id_faktur', 'pembeli__nama', 'vendor__nama', 'kurir__username')
    inlines = [DetailFakturInline]
    autocomplete_fields = ['pembeli', 'vendor', 'kurir']
    readonly_fields = ('total_faktur',)
    actions = ["export_laporan_faktur_pdf"]

    def get_kurir_display(self, obj):
        return obj.kurir.get_full_name() or obj.kurir.username
    get_kurir_display.short_description = 'Kurir'

    # ========== ACTION CETAK PDF (Versi Final) ==========
    def export_laporan_faktur_pdf(self, request, queryset):
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=laporan_faktur.pdf"

        # Konfigurasi dokumen PDF
        doc = SimpleDocTemplate(
            response,
            pagesize=landscape(A4),
            leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=60
        )
        styles = getSampleStyleSheet()
        elements = []

        # Judul laporan
        title_style = ParagraphStyle(
            name='CenterTitle',
            fontSize=16,
            alignment=1,  # center
            spaceAfter=20,
            leading=20
        )
        elements.append(Paragraph("LAPORAN DATA FAKTUR TRIO PRIMA LOGISTIK", title_style))
        elements.append(Spacer(1, 12))

        faktur_list = queryset if queryset else Faktur.objects.all()

        # Header tabel (tanpa kolom ID Faktur)
        data = [["No", "Pembeli", "Vendor", "Kurir", "Status", "Total", "Barang (Detail Faktur)"]]

        # Isi tabel dinamis
        for i, faktur in enumerate(faktur_list, start=1):
            details = ", ".join([
                f"{d.barang.nama_barang} ({d.jumlah_barang})"
                for d in faktur.detail.all()
            ])
            data.append([
                str(i),
                faktur.pembeli.nama,
                faktur.vendor.nama,
                faktur.kurir.username,
                faktur.status,
                f"Rp {faktur.total_faktur:,.0f}",
                details
            ])

        # Tabel dengan lebar kolom fleksibel
        table = Table(
            data,
            repeatRows=1,
            colWidths=[30, 90, 90, 90, 80, 70, 250]  # menyesuaikan isi dinamis
        )

        # Gaya tabel
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(table)

        # Spacer sebelum tanda tangan
        elements.append(Spacer(1, 40))

        # ========== Bagian tanda tangan “Mengetahui” ==========
        # Gunakan indentasi agar posisi agak ke kanan
        signature_indent = 400  # jarak dari kiri halaman (sesuaikan bila perlu)
        para_style_right = ParagraphStyle(
            name="RightAligned",
            alignment=0,  # kiri, tapi dengan indent
            leftIndent=signature_indent,
            fontSize=11,
            leading=15
        )

        elements.append(Paragraph("Mengetahui,", para_style_right))
        elements.append(Spacer(1, 8))
        elements.append(Paragraph("<b>Pimpinan Trio Prima Logistik</b>", para_style_right))
        elements.append(Spacer(1, 40))
        elements.append(Paragraph("................................................", para_style_right))

        # Bangun dokumen PDF
        doc.build(elements)
        return response

    export_laporan_faktur_pdf.short_description = "Cetak Laporan Faktur (PDF Rapi)"

# =================== KELUHAN ===================
@admin.register(Keluhan)
class KeluhanAdmin(admin.ModelAdmin):
    list_display = ('id_keluhan', 'pembeli', 'isi_keluhan', 'foto_keluhan')
    list_filter = ('pembeli',)
    search_fields = ('pembeli__nama', 'isi_keluhan')
    autocomplete_fields = ['pembeli']


# =================== CUSTOM ADMIN SITE ===================
class MyAdminSite(AdminSite):
    site_header = "Dashboard Trio Prima Logistik"
    site_title = "Manajemen Pengiriman"
    index_title = "Selamat Datang di Sistem Admin Trio Prima Logistik"

    def index(self, request, extra_context=None):
        user = request.user
        if not user.is_authenticated:
            return super().index(request, extra_context)
        if user.is_superuser or user.groups.filter(name='Admin').exists():
            return super().index(request, extra_context)
        elif user.groups.filter(name='Kurir').exists():
            return redirect('/admin/core/faktur/')
        elif user.groups.filter(name='Pimpinan').exists():
            return redirect('/admin/core/faktur/')
        return super().index(request, extra_context)


admin_site = MyAdminSite(name='myadmin')
