import os
import re
import time
import requests
import datetime
import warnings
import pandas as pd
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Ignore Warnings
warnings.filterwarnings('ignore')

class CnnTracker:

    def __init__(self, url):
        ## Set infobar filters and get the driver elements
        chrome_options = Options()
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        browser = webdriver.Chrome(ChromeDriverManager().install())
        browser.get(url)
        try:
            WebDriverWait(browser, 100).until(EC.presence_of_element_located(
                (By.XPATH, """//*[@id="__next"]/div[6]/div/div/div[2]/div[2]/div/div/table/tbody/tr[1]/td[2]""")))
            print("Timeout Exception")

        ## Soup objects
        html = browser.page_source
        self.soup = BeautifulSoup(html, features='lxml')

    def poll_tracker(self):

        ## Get the dates
        classes = list(set([value
                            for element in self.soup.find_all(class_=True)
                            for value in element["class"] if value.find('polling-tablestyles__UpdatedText') > -1]))

        dates = []

        for c in classes:
            date_soup = self.soup.find_all('div', {'class': c})
            for child in date_soup:
                child_text = child.get_text()
                if child_text.find("/") > -1 and child_text.find("-") > -1:
                    date_text = child_text.strip().split("-")[-1]
                    year = str(int(date_text.split("/")[-1]) + 2000)
                    date = int(date_text.split("/")[1]) % 31
                    modified_date = "0" + str(date) if date < 10 else str(date)
                    month = int(date_text.split("/")[0]) % 12
                    modified_month = "0" + str(month) if month < 10 else str(month)

                    modified_date = datetime.datetime.strptime(modified_month + "-" + modified_date + "-" + year,
                                                               '%m-%d-%Y')  # print(modified_date)
                    # print(modified_date)

                    dates.append(modified_date)

        ## Get the poll values
        first_candidate_text = ""
        try:
            first_candidate_text = self.soup.find('div', {'class': 'candidate-tablestyles__CandidateName-sc-8lqksg-2 iOiCzR'}).get_text()
        except Exception as e:
            print("Nothing here1")
        first_candidate = 'JOE BIDEN' if fuzz.token_sort_ratio(first_candidate_text, 'Biden') > fuzz.token_sort_ratio(
            first_candidate_text, 'Trump') else 'Donald Trump'
        second_candidate = "DONALD TRUMP" if first_candidate.find("JOE BIDEN") > -1 else "JOE BIDEN"
        # print(first_candidate)

        ## Polls ##

        classes = list(set([value
                            for element in self.soup.find_all(class_=True)
                            for value in element["class"] if value.find('tablestyles__TableData-sc-6') > -1]))

        poll_values = []

        for c in classes:
            if (self.soup.find_all('', {'class': c})):
                poll_soup = self.soup.find_all('', {'class': c})
                for child in poll_soup:
                    child_text = ""
                    try:
                        child_text = child.get_text()
                    except Exception as e:
                        print("Nothing here")
                    poll_values.append(float(child_text.strip().split('%')[0]))

        poll_values_c1 = poll_values[0:5]
        poll_values_c2 = poll_values[5:10]

        biden_values = poll_values_c1 if first_candidate == 'JOE BIDEN' else poll_values_c2
        trump_values = poll_values_c1 if first_candidate == 'DONALD TRUMP' else poll_values_c2

        poll_dict = {'DATE': dates, 'JOE BIDEN': biden_values, 'DONALD TRUMP': trump_values}
        poll_table = pd.DataFrame(poll_dict)
        poll_table['RUN-DATE'] = str(datetime.datetime.today()).split()[0]

        return poll_table

class RcpTracker:

    def __init__(self, url):
        ## Set infobar filters and get the driver elements
        chrome_options = Options()
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        browser = webdriver.Chrome(ChromeDriverManager().install())
        browser.get(url)
        try:
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, """//*[@id="polling-data-rcp"]/table/tbody/tr[2]/td[1]""")))
        except Exception as e:
            print("Exception Occurred")

        ## Soup objects
        html = browser.page_source
        self.soup = BeautifulSoup(html, features='lxml')


    def poll_tracker(self):

        ## Get the dates
        classes = list(set([value
                            for element in self.soup.find_all(class_=True)
                            for value in element["class"] if value.find('rcpAvg') > -1]))

        date_list = []
        poll_values = []

        spread_candidate = ""
        spread_amount = 0
        spread_sign = ""

        for c in classes:
            if (self.soup.find('', {'class': c})):
                poll_soup = self.soup.find('', {'class': c})
                for child in poll_soup:
                    for gc in child:
                        if gc.name:
                            spread = gc.get_text()
                            if fuzz.token_sort_ratio(spread, 'Biden') > fuzz.token_sort_ratio(spread, 'Trump'):
                                spread_candidate = "Biden"
                            else:
                                spread_candidate = "Trump"

                            ## Spread Sign - Positive or Negative
                            spread_sign = "+" if spread.find('+') > -1 else "-"

                        #### Get Date Of Poll and Poll Values ####
                        elif gc.name is None:
                            text = str(gc)
                            if text.find("/") > -1 and text.find("-") > -1:
                                month_date = text.split("-")[-1].strip()

                                # Year
                                year = "2020"

                                # Date
                                date_text = month_date.split("/")[-1]
                                date = int(date_text) % 31
                                modified_date = "0" + str(date) if date < 10 else str(date)

                                # Month
                                month_text = month_date.split("/")[0]
                                month = int(month_text) % 12
                                modified_month = "0" + str(month) if month < 10 else str(month)

                                modified_date = datetime.datetime.strptime(
                                    modified_month + "-" + modified_date + "-" + year,
                                    '%m-%d-%Y')  # print(modified_date)
                                # print(modified_date)

                                date_list.append(modified_date)

                            else:
                                try:
                                    poll_values.append(float(text.strip()))
                                except Exception as e:
                                    pass

        ## Get the poll values
        biden_value = 0
        trump_value = 0

        if spread_candidate == 'Biden' and spread_sign == "+":
            biden_value = max(poll_values)
            trump_value = min(poll_values)

        elif spread_candidate == 'Biden' and spread_sign == "-":
            biden_value = min(poll_values)
            trump_value = max(poll_values)

        elif spread_candidate == 'Trump' and spread_sign == "+":
            biden_value = min(poll_values)
            trump_value = max(poll_values)

        elif spread_candidate == 'Trump' and spread_sign == "-":
            biden_value = max(poll_values)
            trump_value = min(poll_values)

        ## Final Dataframe ##
        poll_dict = {'DATE': date_list, 'JOE BIDEN': biden_value, 'DONALD TRUMP': trump_value}
        poll_table = pd.DataFrame(poll_dict)
        poll_table['RUN-DATE'] = str(datetime.datetime.today()).split()[0]

        return poll_table




