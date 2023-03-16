import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 

from tournament.tests.workshorse import SeleniumTest
from tournament.tools import add_participants, add_team_members
from tournament.models import TournamentRound, Participant, Result


class TestResults(SeleniumTest):
   
    @classmethod
    def tearDownClass(cls):
        #cls.selenium.quit()
        ""

    def test_team_entry(self):
        """Testing a tournament where data is entered per team"""
        add_participants(self.t1, False, 18, 'api/tests/data/teams.csv')
        driver = self.selenium
        self.login()
        self.get_url('/')
        
        self.assertEqual(10, TournamentRound.objects.count())
        self.assertEqual(18, Participant.objects.count())
        
        WebDriverWait(driver, 5, 0.2).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Richmond Showdown U20"))
        ).click()

        self.pair_round('1')

        pencil = WebDriverWait(driver, 5, 0.2).until(
            EC.presence_of_element_located((By.CLASS_NAME, "bi-pencil"))
        )

        self.assertEqual(9, Result.objects.count())

        # now let's add some results shall we?
        pencil.click()
        self.type_score(2000, 1500, games=4)

        # now we wait for the result to be posted and for updated standings to
        # come back to us through web push. If this doesn't get updated something
        # has gone wrong.
        WebDriverWait(driver, 5, 0.2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "td:nth-of-type(2)"), "4")
        )
        
        self.assertEquals(
            '2000', driver.find_element(By.CSS_SELECTOR, "td:nth-of-type(3)").text
        )
        self.assertEquals(
            '1500', driver.find_element(By.CSS_SELECTOR, "td:nth-of-type(6)").text
        )

        # add another score
        pencil = driver.find_elements(By.CLASS_NAME,'bi-pencil')[1]
        pencil.click()
        self.type_score(1430, 2000, games=0)
        time.sleep(1)
        self.assertEquals(Result.objects.filter(games_won=0).count(), 1)
        
    def test_individual_entry(self):
        """Testing a tournament where data is entered per player"""
        add_participants(self.t2, False, 18, 'api/tests/data/teams.csv')
        add_team_members(tournament=self.t2)

        driver = self.selenium
        self.login()
        self.get_url('/')
        
        WebDriverWait(driver, 5, 0.2).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Richmond Showdown U15"))
        ).click()

        self.pair_round('1')

        pencil = WebDriverWait(driver, 5, 0.2).until(
            EC.presence_of_element_located((By.CLASS_NAME, "bi-pencil"))
        )

        self.assertEqual(9, Result.objects.count())

        # now let's add some results shall we?
        pencil.click()
        self.type_score(400, 500, board=4)

        # now we wait for the result to be posted and for updated standings to
        # come back to us through web push. If this doesn't get updated something
        # has gone wrong.
        WebDriverWait(driver, 5, 0.2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "td:nth-of-type(2)"), "4")
        )
        
        self.assertEquals(
            '2000', driver.find_element(By.CSS_SELECTOR, "td:nth-of-type(3)").text
        )
        self.assertEquals(
            '1500', driver.find_element(By.CSS_SELECTOR, "td:nth-of-type(6)").text
        )

        # add another score
        pencil = driver.find_elements(By.CLASS_NAME,'bi-pencil')[1]
        pencil.click()
        self.type_score(430, 500, board=4)
        time.sleep(120)
        self.assertEquals(Result.objects.filter(games_won=0).count(), 1)        

    def flip(self):
        driver = self.selenium
        WebDriverWait(driver, 5, 0.6).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-test-id='unpair']"))
        ).click()
        WebDriverWait(driver, 5, 0.6).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-test-id='pair']"))
        ).click()
