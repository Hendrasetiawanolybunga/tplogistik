from django.db import models
from django.conf import settings
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth.hashers import make_password

# =============================
# MODEL KECAMATAN
# =============================
class Kecamatan(models.Model):
    id_kecamatan = models.AutoField(primary_key=True)
    nama_kecamatan = models.CharField(max_length=100)

    def __str__(self):
        return self.nama_kecamatan

    class Meta:
        verbose_name = "Kecamatan"
        verbose_name_plural = "Kecamatan"


# =============================
# MODEL KELURAHAN
# =============================
class Kelurahan(models.Model):
    id_kelurahan = models.AutoField(primary_key=True)
    nama_kelurahan = models.CharField(max_length=100)
    kode_pos = models.CharField(max_length=10)
    kecamatan = models.ForeignKey(Kecamatan, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nama_kelurahan}, Kec. {self.kecamatan.nama_kecamatan}"

    class Meta:
        verbose_name = "Kelurahan"
        verbose_name_plural = "Kelurahan"


# =============================
# MODEL PEMBELI
# =============================
class Pembeli(models.Model):
    id_pembeli = models.AutoField(primary_key=True)
    nama = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    alamat = models.TextField()
    no_hp = models.CharField(max_length=20)
    kelurahan = models.ForeignKey('Kelurahan', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # Cek apakah password adalah teks biasa (yaitu, belum di-hash)
        # Cara paling sederhana: Cek apakah nilainya terlihat seperti hash
        # Jika password TIDAK diawali dengan format hash (misalnya 'pbkdf2_sha256$'), 
        # maka hash password baru.
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
   

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name = "Pembeli"
        verbose_name_plural = "Pembeli"


# =============================
# MODEL VENDOR
# =============================
class Vendor(models.Model):
    id_vendor = models.AutoField(primary_key=True)
    nama = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100, blank=True, null=True)
    alamat = models.TextField()
    no_hp = models.CharField(max_length=20)

    def save(self, *args, **kwargs):
        # Cek apakah password adalah teks biasa
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
   

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name = "Vendor"
        verbose_name_plural = "Vendor"


# =============================
# MODEL KATEGORI
# =============================
class Kategori(models.Model):
    id_kategori = models.AutoField(primary_key=True)
    nama = models.CharField(max_length=100)

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategori"


# =============================
# MODEL BARANG
# =============================
class Barang(models.Model):
    id_barang = models.AutoField(primary_key=True)
    nama_barang = models.CharField(max_length=100)
    harga_barang = models.DecimalField(max_digits=12, decimal_places=2)
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE)

    def __str__(self):
        return self.nama_barang

    class Meta:
        verbose_name = "Barang"
        verbose_name_plural = "Barang"


# =============================
# MODEL KURIR (Baru)
# =============================
class Kurir(models.Model):
    id_kurir = models.AutoField(primary_key=True)
    nama = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=10)
    no_hp = models.CharField(max_length=20, blank=True, null=True)
    alamat = models.TextField(blank=True, null=True)
    aktif = models.BooleanField(default=True)
    tanggal_bergabung = models.DateField(default=timezone.now)

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name = "Kurir"
        verbose_name_plural = "Kurir"


# =============================
# MODEL FAKTUR
# =============================
class Faktur(models.Model):
    STATUS_CHOICES = [
        ('diproses', 'Diproses'),
        ('selesai', 'Selesai'),
        ('dibatalkan', 'Dibatalkan'),
    ]

    id_faktur = models.AutoField(primary_key=True)
    total_faktur = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='diproses')
    berat = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    koli = models.IntegerField(default=0)
    foto_pengiriman = models.ImageField(upload_to='faktur_images/', blank=True, null=True)
    
    # 🔹 Ganti field kurir agar ambil dari model Kurir baru
    kurir = models.ForeignKey(Kurir, on_delete=models.SET_NULL, null=True, blank=True, related_name='faktur')

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='faktur')
    pembeli = models.ForeignKey(Pembeli, on_delete=models.CASCADE, related_name='faktur')

    def __str__(self):
        return f"Faktur #{self.id_faktur} - {self.pembeli.nama}"

    def update_total(self):
        """Hitung ulang total faktur berdasarkan detailnya."""
        total = Decimal('0.00')
        for detail in self.detail.all():
            total += detail.barang.harga_barang * detail.jumlah_barang
        self.total_faktur = total
        self.save(update_fields=['total_faktur'])

    class Meta:
        verbose_name = "Faktur"
        verbose_name_plural = "Faktur"


# =============================
# MODEL DETAIL FAKTUR
# =============================
class DetailFaktur(models.Model):
    id_detail = models.AutoField(primary_key=True)
    faktur = models.ForeignKey(Faktur, on_delete=models.CASCADE, related_name='detail')
    barang = models.ForeignKey(Barang, on_delete=models.CASCADE, related_name='detail')
    jumlah_barang = models.IntegerField()

    def __str__(self):
        return f"{self.barang.nama_barang} x {self.jumlah_barang}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.faktur.update_total()

    def delete(self, *args, **kwargs):
        faktur = self.faktur
        super().delete(*args, **kwargs)
        faktur.update_total()

    class Meta:
        verbose_name = "Detail Faktur"
        verbose_name_plural = "Detail Faktur"


# =============================
# MODEL KELUHAN
# =============================
class Keluhan(models.Model):
    id_keluhan = models.AutoField(primary_key=True)
    pembeli = models.ForeignKey(Pembeli, on_delete=models.CASCADE)
    faktur = models.CharField(max_length=100, blank=True, null=True)
    isi_keluhan = models.TextField()
    foto = models.ImageField(upload_to='keluhan_images/', blank=True, null=True)
    tanggal = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Keluhan {self.pembeli.nama} - {self.faktur if self.faktur else 'Tanpa Faktur'}"

    class Meta:
        verbose_name = "Keluhan"
        verbose_name_plural = "Keluhan"
