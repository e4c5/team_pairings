# use selenium to create a sample database
import csv
from selenium.webdriver.common.by import By

def add_participants(driver, tournament):
    with open('api/tests/data/teams.csv') as fp:
        name = driver.fine_element(By.CSS_SELECTOR('input[data-test-id=name]'))
        seed = driver.fine_element(By.CSS_SELECTOR('input[data-test-id=seed]'))
        btn = driver.fine_element(By.CSS_SELECTOR('input[data-test-id=add]'))

        reader = csv.reader(fp)
        for line in reader:
            name.send_keys(line[0])
            seed.send_keys(line[1])
            btn.click()
            name.clear()
            seed.clear()
            

