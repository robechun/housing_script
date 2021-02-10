from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from urllib.request import urlretrieve
import dictdiffer
import os


def getStuff(url, prefix):
    # initialize the driver and open the Chrome browser
    driver = webdriver.Chrome('/Users/robechun/Desktop/chromedriver')

    # open the webpage in the current driver
    driver.get(url)
    time.sleep(5)

    WebDriverWait(driver, 60).until(EC.frame_to_be_available_and_switch_to_it(driver.find_element_by_xpath('//iframe[@id="rp-leasing-widget"]')))

    floor_plan_dir = os.getcwd() + '/floor_plans'

    current_floorplans = os.listdir(floor_plan_dir)

    # rows = WebDriverWait(driver, 60).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'floorplan-tile')))

    # for row in rows:
        # row_soup = BeautifulSoup(row.get_attribute('innerHTML'), "html.parser")
        # img_div = row_soup.find('div', class_='loaded-image')
        # plan_url = img_div.attrs['style'].split('(')[1].split(')')[0].replace('"','').replace('320x320','1024x1024')
        # file_name = row_soup.find('span', class_='specs').text.split('|')[0].replace(' ','_') + \
                                    # row_soup.find('span', class_='specs').text.split('|')[1].strip().replace(' ','_') + \
                                    # row_soup.find('span', class_='specs').text.split('|')[2].replace(' ','_') + plan_url[-4:]
        # if file_name not in current_floorplans: 
            # urlretrieve(plan_url, floor_plan_dir + file_name)


    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, 'button')))
    time.sleep(5)

    rows = driver.find_elements_by_tag_name('button')

    if rows[0].get_attribute('innerHTML') == 'Start': 
        rows[0].click()

    elem = driver.find_element_by_class_name('help-div')
    elem.find_element_by_tag_name('a').click()

    rows = driver.find_elements_by_tag_name('button')
    row_count = len(rows)

    i = 0


    units = {}
    y_units = {}

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    f_0 = open(str(yesterday) + prefix + '.txt', 'a+')
    f  = open(str(today) + prefix + '.txt', 'a+')
    f_prime = open(str(today) + prefix + '_diff.txt', 'a+')


    f_0.seek(0)
    y_lines = f_0.readlines()

    for line in y_lines:
        split = line.split(',')
        y_units[split[0]] = line


    for i in range(row_count): 
        rows = WebDriverWait(driver, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'button')))
        if 'Available' in rows[i].get_attribute('innerHTML'):
            rows[i].click()
            
            unit_data = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'data-table')))
            data_soup = BeautifulSoup(unit_data.get_attribute('innerHTML'), "html.parser")
            beds  = data_soup.text.split('Bedrooms')[1].split('Bathrooms')[0]
            baths = data_soup.text.split('Bathrooms')[1].split('Square')[0]
            unit_sf = data_soup.text.split('Feet')[1].split('Occupancy')[0]

            available_rows = driver.find_elements_by_class_name('radio-option')
            for available_unit in available_rows: 
                if 'aria-label' in available_unit.get_attribute('innerHTML'): 
                    row_soup = BeautifulSoup(available_unit.get_attribute('innerHTML'), "html.parser")
                    unit_num  = row_soup.find('span', class_='unit-cell').text
                    unit_rent = row_soup.find('span', class_='unit-price').text

                    out_text = unit_num + ', ' + beds + ', ' + baths + ', ' + unit_sf + ', ' + unit_rent + '\n'
                    units[unit_num] = out_text

                    f.write(out_text)
                            
            time.sleep(1.5)
            back_button = driver.find_element_by_id('footer-back-button')
            back_button.click()
            i += 1
        else:
            i += 1

    prime = list(dictdiffer.diff(y_units, units))

    for l in prime:
        f_prime.write(str(l) + '\n')

    f_0.close()
    f.close()
    f_prime.close()
    driver.close()

if __name__ == '__main__':
    vn150 = 'https://150vanness.com/availability'
    vn100 = 'https://1546003.onlineleasing.realpage.com'

    getStuff(vn150, 'vn150')
    getStuff(vn100, 'vn100')
