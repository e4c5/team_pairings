import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 

from tournament.tests.workshorse import SeleniumTest
from tournament.tools import add_participants
from tournament.models import TournamentRound, Participant, Result


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


        WebDriverWait(driver, 5, 0.6).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-test-id='pair']"))
        ).click()

        time.sleep(0.3)
        self.assertEqual(9, Result.objects.count())
        for r in Result.objects.all():
            print(r.id)

        # now let's add some results shall we?
        WebDriverWait(driver, 5, 0.2).until(
            EC.presence_of_element_located((By.CLASS_NAME, "bi-pencil"))
        ).click()

        driver.find_element(By.CSS_SELECTOR, 'input[data-test-id=games-won]').send_keys(4);
        driver.find_element(By.CSS_SELECTOR, 'input[data-test-id=score1]').send_keys(2000);
        driver.find_element(By.CSS_SELECTOR, 'input[data-test-id=score2]').send_keys(1500);
        driver.find_element(By.CSS_SELECTOR, '.bi-plus').click()

        time.sleep(1)
        # now we wait for the result to be posted and for updated standings to
        # come back to us through web push. If this doesn't get updated something
        # has gone wrong.
        WebDriverWait(driver, 5, 0.2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "td:nth-of-type(1)"), "4")
        )
        time.sleep(100)
        self.assertEquals(
            2000, driver.get(By.CSS_SELECTOR, "td:nth-of-type(2)").text
        )
        self.assertEquals(
            1500, driver.get(By.CSS_SELECTOR, "td:nth-of-type(5)").text
        )

        time.sleep(1)

    def next_one(self):
        pass
        # WebDriverWait(driver, 5, 0.6).until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-test-id='unpair']"))
        # ).click()
        # WebDriverWait(driver, 5, 0.6).until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-test-id='pair']"))
        # ).click()
