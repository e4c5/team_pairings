import time
import csv
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User


from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from tournament.models import Tournament, Participant
# Create your tests here.

class TestParticipants(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Chrome()
        cls.selenium.maximize_window()
        
    def login(self):
        self.selenium.refresh()
        self.get_url('/accounts/login/')
    
        username_input = self.selenium.find_element(By.ID,"id_login")
        username_input.send_keys('admin')
        password_input = self.selenium.find_element(By.ID,"id_password")
        password_input.send_keys('12345')
        
        self.selenium.find_element(By.CSS_SELECTOR,".primaryAction").click()
        
            

    def setUp(self):
        # @todo, change to normal login
        super().setUp()
        u = User(username='admin',is_superuser=True)
        u.set_password('12345')
        u.save()

        self.t1 = Tournament.objects.create(name='Richmond Showdown U20', start_date='2023-02-25',
            rated=False, team_size=5, entry_mode='T', num_rounds=5)


    def get_url(self, relative_path):
        self.selenium.get('%s%s' % (self.live_server_url, relative_path))


    def test_no_forms(self):
        driver = self.selenium
        self.get_url('/')
        
        WebDriverWait(driver, 5, 0.2).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Richmond Showdown U20"))
        ).click()

        WebDriverWait(driver, 5, 0.2).until(
            EC.presence_of_element_located((By.LINK_TEXT, "5"))
        )

        with self.assertRaises(NoSuchElementException) as e:
            driver.find_element(By.CSS_SELECTOR,'input[data-test-id=name]')

        self.assertIsNotNone(e)


    def test_tournament(self):
        driver = self.selenium
        self.login()
        self.get_url('/')

        WebDriverWait(driver, 5, 0.2).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Richmond Showdown U20"))
        ).click()

        self.add_participants()
        self.assertEquals(18, Participant.objects.count())
        self.delete_participants()
        time.sleep(0.2)
        self.assertEquals(0, Participant.objects.count())

        
    def delete_participants(self):
        driver = self.selenium
        buttons = driver.find_elements(By.XPATH, '//button[text()="Del"]')
        for button in reversed(buttons):
            button.click()


    def add_participants(self):
        driver = self.selenium
        with open('api/tests/data/teams.csv') as fp:
            name = WebDriverWait(driver, 5, 0.2).until(
                EC.presence_of_element_located((By.ID,':r0:'))
            )

            seed = driver.find_element(By.ID,':r1:')
            btn = driver.find_element(By.CSS_SELECTOR,'button[data-test-id=add]')

            reader = csv.reader(fp)
            for line in reader:
                name.send_keys(line[0])
                seed.send_keys(line[1])
                btn.click()
                time.sleep(0.1)
                
            

