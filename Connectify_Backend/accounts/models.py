from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Custom User model that extends Django's AbstractUser.
    Adds a role field to distinguish between different types of users.
    """
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        STAFF = 'STAFF', _('Staff')
        USER = 'USER', _('User')
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
        verbose_name=_('Role'),
        help_text=_('Designates the role of this user in the system')
    )
    
    # Add any additional fields here
    
    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
