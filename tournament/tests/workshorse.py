from channels.testing import ChannelsLiveServerTestCase
from django.contrib.auth.models import User

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from tournament.models import Tournament, Participant, Director

class SeleniumTest(ChannelsLiveServerTestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Chrome()
        cls.selenium.maximize_window()

    def login(self):
        """Some actions you need to be logged in"""
        self.selenium.refresh()
        self.get_url('/accounts/login/')
    
        username_input = self.selenium.find_element(By.ID,"id_login")
        username_input.send_keys('admin')
        password_input = self.selenium.find_element(By.ID,"id_password")
        password_input.send_keys('12345')
        
        self.selenium.find_element(By.CSS_SELECTOR,".primaryAction").click()
        

    def setUp(self):
        super().setUp()
        User.objects.all().delete()
        Tournament.objects.all().delete()
        u = User(username='admin',is_superuser=True)
        u.set_password('12345')
        u.save()

        self.t1 = Tournament.objects.create(name='Richmond Showdown U20', start_date='2023-02-25',
            rated=False, team_size=5, entry_mode='T', num_rounds=5)

        Director.objects.create(tournament=self.t1, user=u)

    def get_url(self, relative_path):
        self.selenium.get('%s%s' % (self.live_server_url, relative_path))
