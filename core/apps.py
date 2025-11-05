from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """
        Buat otomatis:
        - Data dummy Kurir (kurir1, kurir2)
        - Group 'Pimpinan' dengan user 'pimpinan1'
        """
        from django.db.utils import OperationalError, ProgrammingError

        try:
            from django.contrib.auth import get_user_model
            from django.contrib.auth.models import Group, Permission
            from django.contrib.contenttypes.models import ContentType
            from .models import Faktur, Kurir  # pastikan Kurir sudah ada di models.py

            User = get_user_model()
            content_type = ContentType.objects.get_for_model(Faktur)

            # ======================================================
            # GROUP DAN USER UNTUK PIMPINAN
            # ======================================================
            pimpinan_group, _ = Group.objects.get_or_create(name='Pimpinan')
            pimpinan_perms = Permission.objects.filter(
                content_type=content_type,
                codename__in=['view_faktur']
            )
            pimpinan_group.permissions.set(pimpinan_perms)

            # Buat user pimpinan
            pimpinan1, created = User.objects.get_or_create(username='pimpinan1')
            if created:
                pimpinan1.set_password('12345')
                pimpinan1.is_staff = True
                pimpinan1.save()
                pimpinan1.groups.add(pimpinan_group)

            # ======================================================
            # DATA DUMMY KURIR (masuk ke model Kurir, bukan User)
            # ======================================================
            dummy_kurirs = [
                {'nama': 'Kurir 1', 'no_hp': '081234567890', 'email': 'kurir1@example.com'},
                {'nama': 'Kurir 2', 'no_hp': '089876543210', 'email': 'kurir2@example.com'},
            ]

            for data in dummy_kurirs:
                Kurir.objects.get_or_create(
                    nama=data['nama'],
                    defaults={
                        'no_hp': data['no_hp'],
                        'email': data['email']
                    }
                )

        except (OperationalError, ProgrammingError):
            # Dijalankan saat awal migrate, tabel belum siap
            pass
