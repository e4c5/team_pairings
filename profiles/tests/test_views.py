from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from profiles.models import Profile

class ConnectViewTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.profile = self.user.profile  # Assuming a Profile model is linked to User
        self.profile.full_name = 'Test User'
        self.profile.preferred_name = 'Test'
        self.profile.save()

    def login(self):
        self.client.login(username='testuser', password='testpass')
        
    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('connect'))  # Assuming the URL name for the connect view is 'connect'
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/accounts/login/?next=' + reverse('connect'))  # Assuming you use Django's built-in login view

    def test_get_request(self):
        self.login()
        resp = self.client.get(reverse('connect'))
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'profiles/connect.html')

    def test_post_request_empty_fields(self):
        self.login()
        resp = self.client.post(reverse('connect'), data={'wespa': '', 'national': '', 'unrated': ''})
        
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.beginner)
        self.assertRedirects(resp, reverse('profile'))  # Assuming the URL name for the profile view is 'profile'
        
    def test_post_request_with_fields(self):
        self.login()
        resp = self.client.post(reverse('connect'), data={'wespa': 'wespa_name', 'national': 'national_name', 'unrated': 'unrated_name'})
        
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.wespa_list_name, 'wespa_name')
        self.assertEqual(self.profile.national_list_name, 'national_name')
        self.assertFalse(self.profile.beginner)
        self.assertRedirects(resp, reverse('profile'))  # Assuming the URL name for the profile view is 'profile'

class EditViewTest(TestCase):
    def test_edit(self):
        u = User.objects.create(username='raditha',first_name='Raditha',last_name='Dissanayake')
        u.set_password('123')
        u.save()
        resp = self.client.get('/profile/edit/')
        self.assertEqual(resp.status_code, 302)
        self.client.login(username='raditha', password='123')
        resp = self.client.get('/profile/edit/')
        self.assertEqual(200, resp.status_code)

        resp = self.client.post('/profile/edit/', 
                                data={'organization': 'UoC', 'phone': 123456789})
        
        self.assertEqual(resp.status_code, 200, resp.context['form'])

        resp = self.client.post('/profile/edit/', 
                                data={'organization': 'UoC', 'phone': +1234567890,
                                      'gender': 'M', 'date_of_birth': '2000-01-01',
                                      'full_name': 'rd', 'display_name': 'xx'
                                      
                                      })
        self.assertEqual(resp.status_code, 302)
        p = Profile.objects.all()[0]

        self.assertEqual(p.organization, 'UoC')
        self.assertEqual(p.phone, '1234567890')

        
