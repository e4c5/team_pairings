import time
import random 

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.action_chains import ActionChains

from tournament.tests.workshorse import SeleniumTest
from tournament.tools import add_participants
from tournament.models import TournamentRound, Participant, Result


class TestIntegrat(SeleniumTest):
    """An full integration test.
    Will setup a tournament, add players. pair rounds, add results
    pair the next round and so on.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.firefox = webdriver.Firefox()


    @classmethod
    def tearDownClass(cls):
        "Sometimes you don't want to quit though "
        cls.selenium.quit()
        cls.firefox.quit()

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
            
        WebDriverWait(driver, 5, 0.6).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-test-id='pair']"))
        ).click()


    def load_tournament(self):
        driver = self.selenium

        ff = self.firefox
        ff.get('%s%s' % (self.live_server_url, '/'))

        self.login()
        self.get_url('/')

        WebDriverWait(driver, 5, 0.2).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Richmond Showdown U20"))
        ).click()

        WebDriverWait(ff, 5, 0.2).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Richmond Showdown U20"))
        ).click()
        

    def add_scores(self):
        driver = self.selenium
        WebDriverWait(driver, 5, 0.2).until(
            EC.presence_of_element_located((By.CLASS_NAME, "bi-pencil"))
        )

        for elem in driver.find_elements(By.CLASS_NAME, "bi-pencil"):
            elem.click()
            
            r = random.randint(0, 5)

            p2 = driver.find_element(By.CSS_SELECTOR, 'input[data-test-id=p2]')         
            # wait for the value of the input field to change from blank to non-blank
            WebDriverWait(driver, 1).until_not(lambda x: p2.get_attribute("value") == "")

            won = driver.find_element(By.CSS_SELECTOR, 'input[data-test-id=games-won]').send_keys(r);
            score1 = random.randint(350, 500) * r
            score2 = random.randint(350, 500) * (5-4)
            driver.find_element(By.CSS_SELECTOR, 'input[data-test-id=score1]').send_keys(score1);
            driver.find_element(By.CSS_SELECTOR, 'input[data-test-id=score2]').send_keys(score2);
            driver.find_element(By.CSS_SELECTOR, '.bi-plus').click()

            # wait for the value of the input field to clear
            WebDriverWait(driver, 1).until(lambda x: p2.get_attribute("value") == "")

    def test_integration(self):
        self.load_tournament()
        self.add_participants()
        self.pair_round('1')
        self.add_scores()

       # time.sleep(100)