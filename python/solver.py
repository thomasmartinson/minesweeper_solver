import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pyautogui as _
from webdriver_manager.driver import OperaDriver

# reveals the cell located at x, y
def reveal(x, y):
  point = driver.find_element_by_id('{}_{}'.format(x+1,y+1)).location
  _.click(point['x']+8, point['y']+8)
  return True

# flag the cell located at x, y
def flag(x,y):
  point = driver.find_element_by_id('{}_{}'.format(x+1,y+1)).location
  _.rightClick(point['x']+8, point['y']+8)
  return True

chrome_options = Options()
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=chrome_options)
driver.get('https://minesweeperonline.com/#200')
driver.fullscreen_window()
time.sleep(5)

flag(1,1)
