from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

## Set infobar filters and get the driver elements
chrome_options = Options()
chrome_options.add_argument("disable-infobars")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
browser = webdriver.Chrome(ChromeDriverManager().install())
browser.get("https://www.cnn.com/election/2020/presidential-polls/arizona")
#browser = webdriver.Chrome(executable_path=r"C:\Users\abhin\OneDrive\Documents\chromedriver_win32\chromedriver.exe", options=chrome_options)
WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, """//*[@id="__next"]/div[6]/div/div/div[2]/div[2]/div/div/table/tbody/tr[1]/td[2]""")))

## Soup objects
html = browser.page_source
soup = BeautifulSoup(html, features='lxml')

classes = [value
           for element in soup.find_all(class_=True)
           for value in element["class"] if value.find() > -1]

print(classes)

class_v = """polling-tablestyles__Row-sc-12yelwa-13 polling-tablestyles__TableDataRow-sc-12yelwa-14 tablestyles__TableDataRow-sc-6vafk0-5 hQTLih"""



