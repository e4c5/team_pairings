import time
import csv

from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from tournament.models import Tournament, Participant, Director
from tournament.tests.workshorse import SeleniumTest

class TestParticipants(SeleniumTest):
        
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

        
    def delete_participants(self):
        """Helper method to delete all participants by clicking del"""
        driver = self.selenium
        buttons = driver.find_elements(By.CLASS_NAME, 'bi-x-circle')
        for button in reversed(buttons):
            button.click()


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
                time.sleep(0.1)

        time.sleep(0.1)
            
            

