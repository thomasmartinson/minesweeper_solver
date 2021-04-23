from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get('https://minesweeperonline.com')

game = driver.find_element_by_a('game')

cells = driver.f ('square')
