from django.db import models
from accounts.models import User
# Create your models here.

class Organization(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    users = models.ManyToManyField(User, related_name='organizations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class OrganizationAdmins(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='organization_admins')
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_organizations')

