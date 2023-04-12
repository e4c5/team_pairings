import time
import random 

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 

from tournament.tests.workshorse import SeleniumTest
from tournament.tools import add_participants
from tournament.models import TournamentRound, Participant, Result


class TestIntegration(SeleniumTest):
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


    def load_tournament(self, name):
        driver = self.selenium

        ff = self.firefox
        ff.get('%s%s' % (self.live_server_url, '/'))

        self.login()
        self.get_url('/')

        WebDriverWait(driver, 5, 0.1).until(
            EC.presence_of_element_located((By.LINK_TEXT, name))
        ).click()

        WebDriverWait(ff, 5, 0.1).until(
            EC.presence_of_element_located((By.LINK_TEXT, name))
        ).click()
        

    def add_scores(self):
        driver = self.selenium
        WebDriverWait(driver, 5, 0.1).until(
            EC.presence_of_element_located((By.CLASS_NAME, "bi-pencil"))
        )

        for elem in driver.find_elements(By.CLASS_NAME, "bi-pencil"):
            elem.click()
            r = random.randint(0, 5)
            score1 = random.randint(350, 500) * r
            score2 = random.randint(350, 500) * (5-4)
            self.type_score(score1, score2, games=r)

    
    def test_integration_of_singles(self):
        """A tournament that's not about teams"""
        self.load_tournament("'New Year Joust'")
        self.add_participants()

    def test_integration_by_board(self):
        """Does the whole hog for a tournament where data entry is by player"""
        self.load_tournament("Richmond Showdown U15")
        self.add_participants()

    def test_integration_by_team(self):
        """Does the whole hog for a tournament where data entry is by team"""
        self.load_tournament("Richmond Showdown U20")
        self.add_participants()
        self.pair_round('1')
        self.add_scores()

        self.pair_round('2')
        self.add_scores()

        self.pair_round('3')
        self.add_scores()

        self.pair_round('4')
        self.add_scores()

        self.pair_round('5')
        self.add_scores()

       # time.sleep(100)