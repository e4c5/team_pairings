import time
import csv
import logging

from channels.testing import ChannelsLiveServerTestCase
from django.contrib.auth.models import User

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.action_chains import ActionChains

from tournament.models import Tournament, Director


class SeleniumTest(ChannelsLiveServerTestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Chrome()
        cls.selenium.maximize_window()

        for handler in logging.getLogger('').handlers:
            if isinstance(handler, logging.StreamHandler):
                logging.getLogger('').removeHandler(handler)

        # Add a file handler for logging to a file
        log_file = '/tmp/test_log_file.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        logging.getLogger('').addHandler(file_handler)

        # Set the log level for Django Channels to DEBUG
        logger = logging.getLogger('django.channels')
        logger.setLevel(logging.DEBUG)

    def login(self):
        """Some actions you need to be logged in"""
        self.selenium.refresh()
        self.get_url('/login/')
    
        username_input = self.selenium.find_element(By.ID,"id_username")
        username_input.send_keys('admin')
        password_input = self.selenium.find_element(By.ID,"id_password")
        password_input.send_keys('12345')
        
        self.selenium.find_element(By.CSS_SELECTOR,".btn-primary").click()
        

    def setUp(self):
        super().setUp()
        User.objects.all().delete()
        Tournament.objects.all().delete()
        u = User(username='admin',is_superuser=True)
        u.set_password('12345')
        u.save()

        self.t1 = Tournament.objects.create(name='Richmond Showdown U20', start_date='2023-02-25',
            rated=False, team_size=5, entry_mode='T', num_rounds=5)
        self.t2 = Tournament.objects.create(name='Richmond Showdown U15', start_date='2023-02-25',
            rated=False, team_size=5, entry_mode='P', num_rounds=5)

        Director.objects.create(tournament=self.t1, user=u)
        Director.objects.create(tournament=self.t2, user=u)

    def get_url(self, relative_path):
        self.selenium.get('%s%s' % (self.live_server_url, relative_path))


    def type_score(self, score1, score2, *, games=None, board=None) :
        driver = self.selenium
        p2 = driver.find_element(By.CSS_SELECTOR, 'input[data-test-id=p2]')         
        # wait for the value of the input field to change from blank to non-blank
        # that's when the react state would have finished updating.
        WebDriverWait(driver, 1, 0.1).until_not(lambda x: p2.get_attribute("value") == "")
        if games is not None:
            driver.find_element(By.CSS_SELECTOR, 'input[data-test-id=games-won]').send_keys(games);
        else:
            driver.find_element(By.CSS_SELECTOR, 'input[data-test-id=board]').send_keys(board);

        driver.find_element(By.CSS_SELECTOR, 'input[data-test-id=score1]').send_keys(score1);
        driver.find_element(By.CSS_SELECTOR, 'input[data-test-id=score2]').send_keys(score2);
        driver.find_element(By.CSS_SELECTOR, '.bi-plus').click()

        # wait for the value of the input field to clear. That's when the data
        # would have been posted to the server , the response recieved and state updated
        WebDriverWait(driver, 1, 0.1).until(lambda x: p2.get_attribute("value") == "")
        
    def add_participants(self):
        """Helper method to load participants in a file by filling forms"""
        driver = self.selenium
        with open('api/tests/data/teams.csv') as fp:
            name = WebDriverWait(driver, 5, 0.2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,'input[data-test-id=name]'))
            )

            rating = driver.find_element(By.CSS_SELECTOR,'input[data-test-id=rating]')
            btn = driver.find_element(By.CSS_SELECTOR,'button[data-test-id=add]')

            reader = csv.reader(fp)
            for line in reader:
                name.send_keys(line[0])
                rating.send_keys(line[1])
                btn.click()
                WebDriverWait(driver, 1, 0.1).until(lambda x: rating.get_attribute("value") == "")

        time.sleep(0.1)
            
    def pair_round(self, rnd):
        driver = self.selenium
        driver.find_element(By.TAG_NAME,'body').send_keys(Keys.END);

        WebDriverWait(driver, 5, 0.2).until(
            EC.visibility_of_element_located((By.LINK_TEXT, rnd))
        )
        try:
            WebDriverWait(driver, 5, 0.2).until(
                EC.element_to_be_clickable((By.LINK_TEXT, rnd))
            ).click()
        except :
            action = ActionChains(driver)
            action.move_to_element(driver.find_element(By.LINK_TEXT, rnd)).click().perform()
            
        WebDriverWait(driver, 5, 0.5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-test-id='pair']"))
        ).click()


    def delete_participants(self):
        """Helper method to delete all participants by clicking del"""
        driver = self.selenium
        buttons = driver.find_elements(By.CLASS_NAME, 'bi-x-circle')
        for button in reversed(buttons):
            button.click()