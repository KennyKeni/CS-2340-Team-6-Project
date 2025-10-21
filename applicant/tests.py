from django.test import TestCase, Client
from django.urls import reverse
from account.models import Account
from applicant.models import Applicant, ProfilePrivacySettings
from recruiter.models import Recruiter
import json


class ProfilePrivacySettingsTestCase(TestCase):
    """Test cases for profile privacy settings"""

    def setUp(self):
        """Set up test data"""
        # Create applicant user
        self.applicant_user = Account.objects.create_user(
            username='testapplicant',
            email='applicant@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Applicant',
            phone_number='1234567890',
            street_address='123 Main St',
            city='Test City',
            state='TS',
            country='Test Country',
            zip_code='12345'
        )
        self.applicant = Applicant.objects.create(
            account=self.applicant_user,
            headline='Software Engineer',
            resume='https://example.com/resume.pdf'
        )

        # Create recruiter user
        self.recruiter_user = Account.objects.create_user(
            username='testrecruiter',
            email='recruiter@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Recruiter',
            street_address='456 Oak Ave',
            city='Test City',
            state='TS',
            country='Test Country',
            zip_code='12345'
        )
        self.recruiter = Recruiter.objects.create(
            account=self.recruiter_user,
            company='Test Company',
            position='HR Manager'
        )

        self.client = Client()

    def test_privacy_settings_creation(self):
        """Test that privacy settings are created with default values"""
        privacy_settings = self.applicant.get_or_create_privacy_settings()
        
        self.assertIsNotNone(privacy_settings)
        self.assertTrue(privacy_settings.show_email)
        self.assertTrue(privacy_settings.show_phone)
        self.assertTrue(privacy_settings.show_resume)
        self.assertTrue(privacy_settings.show_gpa)
        self.assertTrue(privacy_settings.show_current_employment)
        self.assertTrue(privacy_settings.show_current_education)
        self.assertTrue(privacy_settings.visible_to_recruiters)

    def test_view_profile_includes_privacy_settings(self):
        """Test that viewing profile includes privacy settings"""
        self.client.login(username='testapplicant', password='testpass123')
        response = self.client.get(reverse('applicant:view_profile'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('privacy_settings', response.context['template_data'])

    def test_update_privacy_settings_ajax(self):
        """Test updating privacy settings via AJAX"""
        self.client.login(username='testapplicant', password='testpass123')
        
        # Update privacy settings
        privacy_data = {
            'privacy_settings': {
                'visible_to_recruiters': False,
                'show_email': False,
                'show_phone': True,
                'show_resume': False,
                'show_gpa': True,
                'show_current_employment': False,
                'show_current_education': True,
            }
        }
        
        response = self.client.post(
            reverse('applicant:view_profile'),
            data=json.dumps(privacy_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        
        # Verify settings were updated
        privacy_settings = ProfilePrivacySettings.objects.get(applicant=self.applicant)
        self.assertFalse(privacy_settings.visible_to_recruiters)
        self.assertFalse(privacy_settings.show_email)
        self.assertTrue(privacy_settings.show_phone)
        self.assertFalse(privacy_settings.show_resume)

    def test_hidden_profile_not_in_recruiter_search(self):
        """Test that hidden profiles don't appear in recruiter searches"""
        # First, make profile invisible
        privacy_settings = self.applicant.get_or_create_privacy_settings()
        privacy_settings.visible_to_recruiters = False
        privacy_settings.save()
        
        # Login as recruiter and search
        self.client.login(username='testrecruiter', password='testpass123')
        response = self.client.get(reverse('recruiter:candidate_search'))
        
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.applicant, response.context['candidates'])

    def test_visible_profile_in_recruiter_search(self):
        """Test that visible profiles appear in recruiter searches"""
        # Ensure profile is visible
        privacy_settings = self.applicant.get_or_create_privacy_settings()
        privacy_settings.visible_to_recruiters = True
        privacy_settings.save()
        
        # Login as recruiter and search
        self.client.login(username='testrecruiter', password='testpass123')
        response = self.client.get(reverse('recruiter:candidate_search'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.applicant, response.context['candidates'])

    def test_applicant_search_api_respects_privacy(self):
        """Test that API respects privacy settings for recruiters"""
        # Hide email and phone
        privacy_settings = self.applicant.get_or_create_privacy_settings()
        privacy_settings.show_email = False
        privacy_settings.show_phone = False
        privacy_settings.show_resume = False
        privacy_settings.save()
        
        # Login as recruiter and call API
        self.client.login(username='testrecruiter', password='testpass123')
        response = self.client.get(reverse('applicant:applicant_search'))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Find the applicant in results
        applicant_data = next(
            (item for item in data['data'] if item['username'] == 'testapplicant'),
            None
        )
        
        self.assertIsNotNone(applicant_data)
        self.assertEqual(applicant_data['email'], '[Hidden]')
        self.assertEqual(applicant_data['phone_number'], '[Hidden]')
        self.assertEqual(applicant_data['resume'], '[Hidden]')

    def test_applicant_search_api_shows_data_to_applicants(self):
        """Test that API shows full data to other applicants"""
        # Create another applicant
        another_applicant_user = Account.objects.create_user(
            username='otherapplicant',
            email='other@test.com',
            password='testpass123',
            first_name='Other',
            last_name='Applicant',
            street_address='789 Pine St',
            city='Test City',
            state='TS',
            country='Test Country',
            zip_code='12345'
        )
        Applicant.objects.create(account=another_applicant_user)
        
        # Hide email from recruiters
        privacy_settings = self.applicant.get_or_create_privacy_settings()
        privacy_settings.show_email = False
        privacy_settings.save()
        
        # Login as another applicant and call API
        self.client.login(username='otherapplicant', password='testpass123')
        response = self.client.get(reverse('applicant:applicant_search'))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Find the applicant in results
        applicant_data = next(
            (item for item in data['data'] if item['username'] == 'testapplicant'),
            None
        )
        
        self.assertIsNotNone(applicant_data)
        # Applicants should see full email, not hidden
        self.assertEqual(applicant_data['email'], 'applicant@test.com')
