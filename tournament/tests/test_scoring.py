import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 

from tournament.tests.workshorse import SeleniumTest
from tournament.tools import add_participants
from tournament.models import TournamentRound, Participant
class TestResults(SeleniumTest):

    def test_team_entry(self):
        """Testing a tournament where data is entered per team"""
        add_participants(self.t1, False, 18, 'api/tests/data/teams.csv')
        driver = self.selenium
        self.login()
        self.get_url('/')
        
        self.assertEqual(5, TournamentRound.objects.count())
        self.assertEqual(18, Participant.objects.count())
        
        WebDriverWait(driver, 5, 0.2).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Richmond Showdown U20"))
        ).click()

        driver.find_element(By.TAG_NAME,'body').send_keys(Keys.END);

        WebDriverWait(driver, 5, 0.2).until(
            EC.visibility_of_element_located((By.LINK_TEXT, "1"))
        )
        WebDriverWait(driver, 5, 0.2).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "1"))
        ).click()

        WebDriverWait(driver, 5, 0.2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-test-id='pair']"))
        ).click()

        WebDriverWait(driver, 5, 0.2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-test-id='unpair']"))
        ).click()


        time.sleep(1)