from typing import TypeVar
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save

from utils.validators import validate_special_char


T = TypeVar("T", bound=AbstractBaseUser)


class UserManager(BaseUserManager):
    def create_base_user(
        self, username, is_active=True, is_staff=False, is_admin=False
    ) -> T:
        if not username:
            raise ValueError("User must provide an username")

        user: User = self.model(username=username)
        user.active = is_active
        user.admin = is_admin
        user.staff = is_staff
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(
        self, username, password=None, is_active=True, is_staff=False, is_admin=False
    ) -> T:
        user = self.create_base_user(username, is_active, is_staff, is_admin)
        if not password:
            raise ValueError("User must provide a password")
        user.set_password(password)
        user.save()
        return user

    def create_staff(self, username, password=None) -> T:
        user = self.create_user(username=username, password=password, is_staff=True)
        return user

    def create_superuser(self, username, password=None) -> T:
        user = self.create_user(
            username=username, password=password, is_staff=True, is_admin=True
        )
        return user

    def get_staffs(self):
        return self.filter(staff=True)

    def get_admins(self):
        return self.filter(admin=True)


class User(AbstractBaseUser):
    username = models.CharField(
        unique=True, max_length=255, validators=[validate_special_char]
    )

    # Admin fields
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = "username"

    objects = UserManager()

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def __str__(self) -> str:
        return self.username

    @property
    def is_active(self) -> bool:
        return self.active

    @property
    def is_staff(self) -> bool:
        return self.staff

    @property
    def is_admin(self) -> bool:
        return self.admin


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.user.username

    @property
    def username(self) -> str:
        return self.user.username


@receiver(post_save, sender=User)
def create_profile(sender, instance: User, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
