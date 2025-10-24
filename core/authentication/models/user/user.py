from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.TextField(null=True, blank=True, verbose_name='Nombres')
    last_name = models.TextField(null=True, blank=True, verbose_name='Apellidos')
    username = models.TextField(unique=True, verbose_name='Username')
    dni = models.TextField(unique=True, verbose_name='Número de cédula')
    email = models.EmailField(unique=True, verbose_name='Email')
    is_active = models.BooleanField(default=True, verbose_name='Estado')
    is_staff = models.BooleanField(default=False, verbose_name='Staff')
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='Fecha de creacion')

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    @classmethod
    def get_or_create_user(cls, data_user):
        try:
            user, created = cls.objects.get_or_create(
                dni=data_user['dni'],
                defaults={
                    'first_name': data_user.get('first_name', ''),
                    'last_name': data_user.get('last_name', ''),
                    'username': data_user.get('username', data_user['dni']),
                    'email': data_user.get('email', ''),
                    'is_active': True,
                }
            )
            return user
        except Exception as e:
            raise Exception(f'Error creating or getting user: {e}')

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-id']
