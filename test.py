from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import time
class ElementNotFound(Exception):
    def __init__(self):
        pass

edge_options = webdriver.EdgeOptions()

edge_options.add_argument("--enable-chrome-browser-cloud-management")
edge_options.add_experimental_option('excludeSwitches',['enable-logging'])
edge_options.add_experimental_option('detach',True)

ser = Service("edgedriver_mac64/msedgedriver")
edge_browser = webdriver.Edge(options = edge_options)
print('Browsing login-in page')
edge_browser.get("https://www.linkedin.com/login")
#time.sleep(4)
username_xpath = "//form/div/input[@id='username']"
pass_xpath = "//form/div/input[@id='password']"
signin_xpath ="//form/div/button[@class='btn__primary--large from__button--floating']"
e1 = edge_browser.find_element(By.XPATH,username_xpath)
e2 = edge_browser.find_element(By.XPATH,pass_xpath)
e1.send_keys("quynhnguyen.linkedin@gmail.com")
e2.send_keys("khungdien123")
signin_button = edge_browser.find_element(By.XPATH,signin_xpath)
signin_button.click()
edge_browser.get("https://www.linkedin.com/in/bobwebber/recent-activity/all/")

x_path = "//div[@class='update-components-text relative update-components-update-v2__commentary ']/span/span[@dir='ltr']"

e3 = edge_browser.find_elements(By.XPATH,x_path)
print(e3)



