import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from django.contrib.auth.models import User

from tournament.models import Tournament, Participant
# Create your tests here.

class TestParticipants(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Chrome()
        cls.selenium.maximize_window()
        

    def setUp(self):
        # @todo, change to normal login
        super().setUp()
        u = User(username='admin',password='12345',is_superuser=True)
        u.save()

        self.t1 = Tournament.objects.create(name='Richmond Showdown U20', start_date='2023-02-25',
            rated=False, team_size=5, entry_mode='T', num_rounds=5)


    def get_url(self, relative_path):
        self.selenium.get('%s%s' % (self.live_server_url, relative_path))

    def test_tournament(self):
        driver = self.selenium
        self.get_url('/')
        time.sleep(30)