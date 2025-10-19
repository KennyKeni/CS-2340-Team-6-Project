import os
import sys
import django

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_app.settings')
django.setup()

from django.core.mail import send_mail

try:
    send_mail(
        subject='Test Email from DevJobs',
        message='This is a test email to verify Gmail SMTP configuration.',
        from_email=None,  # Will use DEFAULT_FROM_EMAIL
        recipient_list=['linkenny717@gmail.com'],
        fail_silently=False,
    )
    print("✓ Email sent successfully!")
except Exception as e:
    print(f"✗ Email failed with error: {e}")
    import traceback
    traceback.print_exc()
