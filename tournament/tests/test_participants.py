import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from tournament.models import Participant
from tournament.tests.workshorse import SeleniumTest
from tournament.tools import add_participants, random_results, add_team_members

from api import swiss

class TestParticipants(SeleniumTest):
        
    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        ""
    
    def test_no_forms(self):
        """For not authenticated users the edit/create forms would not show up"""
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


    def test_add_delete_participants(self):
        driver = self.selenium
        self.login()
        self.get_url('/')

        WebDriverWait(driver, 5, 0.2).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Richmond Showdown U20"))
        ).click()

        self.add_participants()
        time.sleep(0.2)
        self.assertEquals(18, Participant.objects.count())
        self.delete_participants()
        time.sleep(0.2)
        self.assertEquals(0, Participant.objects.count())


    def test_participant_details(self):
        """Test that the participant details page shows the correct information"""
        partis = add_participants(count=10, use_faker=True, tournament=self.t1)
        self.assertEqual(10, self.t1.participants.count())
        driver = self.selenium
        self.login()
        self.get_url('/')

        rnd = self.t1.rounds.get(round_no=1)
        sp = swiss.SwissPairing(rnd)
        sp.make_it()
        sp.save()

        random_results(self.t1)
        WebDriverWait(driver, 5, 0.2).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Richmond Showdown U20"))
        ).click()

        WebDriverWait(driver, 5, 0.2).until(
            EC.presence_of_element_located((By.LINK_TEXT, partis[0].name))
        ).click()
 
        WebDriverWait(driver, 5, 0.2).until(
            EC.presence_of_element_located((By.CLASS_NAME, "bi-pencil"))
        )
        


