import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import json

PRINT_SCROLL_LOGS_MODIFIER = 20
TOTAL_THRESHOLD = 5
MAX_SCROLLS = 5000
#MAX_SCROLLS = 2

def log(data):
    print(data)

try:
    with open('cookies.json', 'r') as file:
        cookies = json.load(file)
except:
    log('Unable to get cookies')
    cookies = {}

browser = webdriver.Chrome()
browser.get("https://slack.com/signin")

if len(cookies) == 0:
    # Login to slack ( Manual )
    cmd = ''
    while (cmd != 'ready'):
        cmd = input("Type `ready` when login completes and you've opened up the ws:\n> ")
else:
    # Set stored cookies to maintain the session
    for cookie in cookies:
        try:
            browser.add_cookie(cookie)
        except:
            log('Fail to add cookie')

# Save cookies
with open('cookies.json', 'w') as file:
    cookies = browser.get_cookies()
    json.dump(cookies, file)
log('Login complete')

# Go to channel
browser.get("https://app.slack.com/client/TK8V2RL7Q/C01G7CFNA8K")

time.sleep(10)

log('Starting the script now')

