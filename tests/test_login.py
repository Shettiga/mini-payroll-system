from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Start browser
driver = webdriver.Chrome()

# Open your website
driver.get("http://127.0.0.1:5000")

# Maximize window
driver.maximize_window()

# Wait
time.sleep(2)

# Find username field
username = driver.find_element(By.NAME, "username")
username.send_keys("admin")

# Find password field
password = driver.find_element(By.NAME, "password")
password.send_keys("admin")

# Press Enter
password.send_keys(Keys.RETURN)

# Wait to see result
time.sleep(3)

print("Login Test Completed")

driver.quit()
