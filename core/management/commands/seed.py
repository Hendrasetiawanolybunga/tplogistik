from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import (
    Kecamatan, Kelurahan, Pembeli, Vendor, Kategori, Barang,
    Faktur, DetailFaktur, Keluhan
)
from django.db import transaction
from decimal import Decimal
import random


class Command(BaseCommand):
    help = "Seed database dengan data dummy dan setup group + user"

    @transaction.atomic
    def handle(self, *args, **options):
        # 1️⃣ CEK apakah sudah ada data
        if Kecamatan.objects.exists():
            self.stdout.write("❗ Data sudah ada, seeding dibatalkan.")
            return

        # 2️⃣ BERSIHKAN group (optional jika flush sudah dilakukan)
        Group.objects.all().delete()

        # 3️⃣ BUAT GROUPS
        grup_admin, _ = Group.objects.get_or_create(name="Admin")
        grup_kurir, _ = Group.objects.get_or_create(name="Kurir")
        grup_pimpinan, _ = Group.objects.get_or_create(name="Pimpinan")

        # 4️⃣ BUAT PERMISSION OTOMATIS UNTUK MASING-MASING GROUP
        # Admin: semua permission
        all_perms = Permission.objects.all()
        grup_admin.permissions.set(all_perms)

        # Kurir: hanya bisa view dan change Faktur (untuk update status & upload foto)
        faktur_ct = ContentType.objects.get_for_model(Faktur)
        perm_view_faktur = Permission.objects.get(codename="view_faktur", content_type=faktur_ct)
        perm_change_faktur = Permission.objects.get(codename="change_faktur", content_type=faktur_ct)
        grup_kurir.permissions.set([perm_view_faktur, perm_change_faktur])

        # Pimpinan: hanya bisa view semua model
        view_perms = Permission.objects.filter(codename__startswith="view_")
        grup_pimpinan.permissions.set(view_perms)

        # 5️⃣ BUAT USER
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={"is_staff": True, "is_superuser": True, "email": "admin@example.com"}
        )
        admin_user.set_password("admin123")
        admin_user.save()
        admin_user.groups.add(grup_admin)

        kurir_user, _ = User.objects.get_or_create(
            username="kurir1",
            defaults={"is_staff": True, "email": "kurir@example.com"}
        )
        kurir_user.set_password("kurir123")
        kurir_user.save()
        kurir_user.groups.add(grup_kurir)

        pimpinan_user, _ = User.objects.get_or_create(
            username="pimpinan",
            defaults={"is_staff": True, "email": "pimpinan@example.com"}
        )
        pimpinan_user.set_password("pimpinan123")
        pimpinan_user.save()
        pimpinan_user.groups.add(grup_pimpinan)

        # 6️⃣ DATA KECAMATAN, KELURAHAN, PEMBELI, VENDOR, DLL
        kec1 = Kecamatan.objects.create(nama_kecamatan="Oebobo")
        kec2 = Kecamatan.objects.create(nama_kecamatan="Kelapa Lima")

        kel1 = Kelurahan.objects.create(nama_kelurahan="Oebufu", kode_pos="85111", kecamatan=kec1)
        kel2 = Kelurahan.objects.create(nama_kelurahan="Fatululi", kode_pos="85112", kecamatan=kec1)
        kel3 = Kelurahan.objects.create(nama_kelurahan="Namosain", kode_pos="85113", kecamatan=kec2)

        pemb1 = Pembeli.objects.create(nama="Verel", alamat="Jl. Perintis", no_hp="081234567890", kelurahan=kel1)
        pemb2 = Pembeli.objects.create(nama="Andi", alamat="Jl. Cakra", no_hp="081298765432", kelurahan=kel2)

        vendor1 = Vendor.objects.create(nama="CV Sumber Rejeki", email="cv@rejeki.com", alamat="Jl. Sam Ratulangi", no_hp="08111222333")
        vendor2 = Vendor.objects.create(nama="PT Warisan Enak", email="info@warisanenak.com", alamat="Jl. Eltari", no_hp="08199887766")

        kat1 = Kategori.objects.create(nama="Minuman")
        kat2 = Kategori.objects.create(nama="Makanan")

        barang1 = Barang.objects.create(nama_barang="Susu Jahe", harga_barang=Decimal("25000.00"), kategori=kat1)
        barang2 = Barang.objects.create(nama_barang="Susu Kedelai", harga_barang=Decimal("20000.00"), kategori=kat1)
        barang3 = Barang.objects.create(nama_barang="Keripik Pisang", harga_barang=Decimal("15000.00"), kategori=kat2)

        # 7️⃣ DATA FAKTUR DAN DETAILNYA
        for i in range(3):
            faktur = Faktur.objects.create(
                total_faktur=Decimal(random.randint(30000, 100000)),
                status=random.choice(["diproses", "selesai"]),
                berat=Decimal(random.uniform(1.0, 5.0)),
                koli=random.randint(1, 5),
                foto_pengiriman="faktur_images/default.jpg",
                kurir=kurir_user,
                vendor=random.choice([vendor1, vendor2]),
                pembeli=random.choice([pemb1, pemb2])
            )
            DetailFaktur.objects.create(faktur=faktur, barang=barang1, jumlah_barang=2)
            DetailFaktur.objects.create(faktur=faktur, barang=barang2, jumlah_barang=1)

        # 8️⃣ DATA KELUHAN
        Keluhan.objects.create(isi_keluhan="Produk tidak sesuai pesanan", pembeli=pemb1)
        Keluhan.objects.create(isi_keluhan="Pengiriman terlambat", pembeli=pemb2)

        self.stdout.write(self.style.SUCCESS("✅ Berhasil menambahkan data dummy dan setup grup + user."))
