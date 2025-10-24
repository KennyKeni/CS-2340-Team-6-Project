import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_app.settings')
django.setup()

from account.models import Account

username = 'admin'
email = 'admin@example.com'
password = 'admin123'

if not Account.objects.filter(username=username).exists():
    Account.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser created successfully!")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Email: {email}")
else:
    print(f"User '{username}' already exists.")
