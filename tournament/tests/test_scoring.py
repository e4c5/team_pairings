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

    def test_tsh_style_entry(self):
        """Test data entry with TSH style"""
        add_participants(self.t3, True, 6, seed=10)
        Participant.objects.update(approval='V')

        driver = self.load_tournament('New Year Joust')
        self.assertEqual(Result.objects.count(), 0)
        self.pair_round('1')
        WebDriverWait(driver, 5, 0.1).until(
            EC.presence_of_element_located((By.CLASS_NAME, "bi-pencil"))
        )
        self.assertEqual(3, Result.objects.count())

        field = driver.find_element(By.CSS_SELECTOR, "input[data-testid='tsh-style-entry']")
        field.click()
        field.send_keys('ames 439 mirez 410')
        field.send_keys(Keys.ENTER)

        time.sleep(0.5)

        result = driver.find_element(By.XPATH,"//td[contains(text(), 'James')]")
        result = result.find_element(By.XPATH,'following-sibling::*[1]')
        self.assertEqual(result.text, '1')

        field.click()
        field.send_keys('4 444 3 333')
        field.send_keys(Keys.ENTER)

        time.sleep(0.5)

        result = driver.find_element(By.XPATH,"//td[contains(text(), 'Murphy')]")
        result = result.find_element(By.XPATH,'following-sibling::*[1]')
        self.assertEqual(result.text, '0')
        

    def test_autocomplete(self):
        """Test data entry with autocomplete"""
        add_participants(self.t3, True, 6, seed=10)
        driver = self.load_tournament('New Year Joust')
        self.assertEqual(Result.objects.count(), 0)
        self.pair_round('1')
        WebDriverWait(driver, 5, 0.1).until(
            EC.presence_of_element_located((By.CLASS_NAME, "bi-pencil"))
        )
        self.assertEqual(3, Result.objects.count())
        field = driver.find_element(By.CSS_SELECTOR, "input[data-testid='autocomplete']")
        field.click()
        field.send_keys('Debo')
        field.send_keys(Keys.ENTER)
        field.send_keys(Keys.TAB)
        field = driver.switch_to.active_element

        field.send_keys("444")
        field.send_keys(Keys.TAB)
        field = driver.switch_to.active_element
        
        field.send_keys("333")
        field.send_keys(Keys.ENTER)
        field.send_keys(Keys.TAB)
        field = driver.switch_to.active_element
        
        field.send_keys(Keys.ENTER)
        time.sleep(1)

        result = driver.find_element(By.XPATH,"//td[contains(text(), 'Deborah')]")
        result = result.find_element(By.XPATH,'following-sibling::*[1]')

        self.assertEqual(result.text, '1')


    def test_singles_entry(self):
        """Test data entry by clicking on the edit icon"""
        add_participants(self.t3, True, 5)

        driver = self.load_tournament('New Year Joust')
        self.assertEqual(Result.objects.count(), 0)
        
        self.pair_round('1')

        WebDriverWait(driver, 5, 0.1).until(
            EC.presence_of_element_located((By.CLASS_NAME, "bi-pencil"))
        )
         
        self.assertEqual(3, Result.objects.count())
        pencils = driver.find_elements(By.CLASS_NAME, "bi-pencil")

        pencils[1].click()
        self.type_score(547, 369)

        pencils[2].click()
        self.type_score(497, 315)

        self.pair_round('2')
        


    def test_team_entry(self):
        """Testing a tournament where data is entered per team"""
        add_participants(self.t1, False, 18, 'api/tests/data/teams.csv')
        self.assertEqual(19, TournamentRound.objects.count())
        self.assertEqual(18, Participant.objects.count())
        time.sleep(0.1)
        self.load_tournament("Richmond Showdown U20")
        Participant.objects.update(approval='V')
        self.pair_round('1')
        driver = self.selenium
        
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
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "td:nth-of-type(3)"), "4")
        )
        
        self.assertEquals(
            '2000', driver.find_element(By.CSS_SELECTOR, "td:nth-of-type(4)").text
        )
        self.assertEquals(
            '1500', driver.find_element(By.CSS_SELECTOR, "td:nth-of-type(7)").text
        )

        # add another score
        pencil = driver.find_elements(By.CLASS_NAME,'bi-pencil')[1]
        pencil.click()
        self.type_score(1430, 2000, games=0)
        time.sleep(1)
        self.assertEquals(Result.objects.filter(games_won=0).count(), 1)
        

    def test_entry_by_player(self):
        """Testing a tournament where data is entered per player"""
        add_participants(self.t2, False, 18, 'api/tests/data/teams.csv')
        Participant.objects.update(approval='V')
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
        table = driver.find_element(By.ID, "results")
        WebDriverWait(table, 5, 0.2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "td:nth-of-type(3)"), "0")
        )
        
        self.assertEquals(
            '400', table.find_element(By.CSS_SELECTOR, "td:nth-of-type(4)").text
        )
        self.assertEquals(
            '500', table.find_element(By.CSS_SELECTOR, "td:nth-of-type(7)").text
        )

        # add another score
        pencil = driver.find_elements(By.CLASS_NAME,'bi-pencil')[1]
        pencil.click()
        self.type_score(430, 500, board=4)
        tr = table.find_element(By.CSS_SELECTOR, "tr:nth-of-type(2)")
        self.assertEquals(
            '430', tr.find_element(By.CSS_SELECTOR, "td:nth-of-type(4)").text
        )
        self.assertEquals(Result.objects.filter(games_won=0).count(), 2)        


    def flip(self):
        driver = self.selenium
        WebDriverWait(driver, 5, 0.6).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='unpair']"))
        ).click()
        WebDriverWait(driver, 5, 0.6).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='pair']"))
        ).click()
