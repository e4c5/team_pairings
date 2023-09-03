from django.test.testcases import TestCase
from django.contrib.auth import get_user_model
from profiles.models import Profile


User = get_user_model()

class ProfileTest(TestCase):

    def  test_profile(self):
        """Test if the profile is created"""
        
        User.objects.create(username='raditha',first_name='Raditha',last_name='Dissanayake')
        self.assertEqual(User.objects.count(),1)
        self.assertEqual(Profile.objects.count(),1)
        prof = Profile.objects.all()[0]
        self.assertEqual(prof.player_id, 'RDISS')
        self.assertEqual(prof.user.username, 'raditha')

        User.objects.create(username='radinka',first_name='Radinka',last_name='Dissanayake')
        prof = Profile.objects.all()[1]
        self.assertEqual(prof.player_id, 'RADIS')
        self.assertEqual(prof.user.username, 'radinka')


    def test_with_short_name(self):
        User.objects.create(username='a',first_name='a',last_name='b')
        prof = Profile.objects.all()[0]
        self.assertEqual(prof.player_id, 'AB')

    