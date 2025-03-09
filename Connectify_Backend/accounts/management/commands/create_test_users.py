from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = 'Creates test users with different roles'

    def handle(self, *args, **options):
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin_test',
            email='admin@example.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Admin user created: {admin_user.username}'))
        else:
            self.stdout.write(self.style.WARNING(f'Admin user already exists: {admin_user.username}'))
        
        # Create regular user
        regular_user, created = User.objects.get_or_create(
            username='user_test',
            email='user@example.com',
            defaults={
                'first_name': 'Regular',
                'last_name': 'User',
                'role': User.Role.USER,
                'is_staff': False,
                'is_superuser': False,
            }
        )
        
        if created:
            regular_user.set_password('user123')
            regular_user.save()
            self.stdout.write(self.style.SUCCESS(f'Regular user created: {regular_user.username}'))
        else:
            self.stdout.write(self.style.WARNING(f'Regular user already exists: {regular_user.username}'))
            
        self.stdout.write(self.style.SUCCESS('Test users created successfully!'))
        self.stdout.write(self.style.SUCCESS('Admin user: username=admin_test, password=admin123'))
        self.stdout.write(self.style.SUCCESS('Regular user: username=user_test, password=user123')) 