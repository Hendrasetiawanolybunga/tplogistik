from django.db import models
from django.conf import settings
from decimal import Decimal


class Kecamatan(models.Model):
    id_kecamatan = models.AutoField(primary_key=True)
    nama_kecamatan = models.CharField(max_length=100)

    def __str__(self):
        return self.nama_kecamatan

    class Meta:
        verbose_name = "Kecamatan"
        verbose_name_plural = "Kecamatan"


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


class Pembeli(models.Model):
    id_pembeli = models.AutoField(primary_key=True)
    nama = models.CharField(max_length=100)
    alamat = models.TextField()
    no_hp = models.CharField(max_length=20)
    kelurahan = models.ForeignKey(Kelurahan, on_delete=models.CASCADE)

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name = "Pembeli"
        verbose_name_plural = "Pembeli"


class Vendor(models.Model):
    id_vendor = models.AutoField(primary_key=True)
    nama = models.CharField(max_length=100)
    email = models.EmailField()
    alamat = models.TextField()
    no_hp = models.CharField(max_length=20)

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name = "Vendor"
        verbose_name_plural = "Vendor"


class Kategori(models.Model):
    id_kategori = models.AutoField(primary_key=True)
    nama = models.CharField(max_length=100)

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategori"


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
    kurir = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='faktur_kurir')
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


class Keluhan(models.Model):
    id_keluhan = models.AutoField(primary_key=True)
    isi_keluhan = models.TextField()
    foto_keluhan = models.ImageField(upload_to='keluhan_images/', blank=True, null=True)
    pembeli = models.ForeignKey(Pembeli, on_delete=models.CASCADE)

    def __str__(self):
        return f"Keluhan #{self.id_keluhan} - {self.pembeli.nama}"

    class Meta:
        verbose_name = "Keluhan"
        verbose_name_plural = "Keluhan"
