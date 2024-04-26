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

def delay(browser, time):
    browser.execute_script('''
        const delay = async (time) => {
            await new Promise((resolve, _) => {
                setTimeout(() => {
                resolve(true);
                }, time);
            });
        };
    ''' + f'delay({time})')

def navigateToChannel(browser, channelName):
    browser.execute_script('''
        async function navigateToChannel(channelName) {
            const channels = document.querySelectorAll('.p-channel_sidebar__static_list__item');
            const channel = Array.from(channels).find((channel) => channel.innerText === channelName);
            channel.click();
        }
    ''' + f'navigateToChannel("{channelName}")')

def openMemberListForCurrentChannel(browser):
    browser.execute_script('''
        async function openMemberListForCurrentChannel() {
            const openMemberListBtn = document.querySelector('.p-avatar_stack--details');

            openMemberListBtn.click();
        };
    ''' + 'openMemberListForCurrentChannel();')

def getNumberOfUsers(browser):
    numberOfUsers = browser.execute_script('''
        try {
            const countEle = document.querySelector('.c-tabs__tab_count');
            return Number(countEle.innerText);
        } catch (err) {
            return 0;
        }
    ''')
    return numberOfUsers

def getUserNames(browser):
    users = browser.execute_script('''
        namesMap = {}
        let numberOfUsers;
        membersListEle = document.querySelector('.p-ia_details_popover__members_list')
        scroller = membersListEle.querySelector('.c-scrollbar__hider');
        try {
            const countEle = document.querySelector('.c-tabs__tab_count');
            numberOfUsers = Number(countEle.innerText);
        } catch {
            numberOfUsers = 0;
        }

        while (Object.keys(namesMap).length < numberOfUsers) {
            scroller.scrollBy({ top: 200, behavior: 'smooth'});

            let currentMemberEles = membersListEle.querySelectorAll('.p-ia_details_popover__members_list_item_member')
            for (let i = 0; i < currentMemberEles.length; i++) {
                try {
                    const currentMemberEle = currentMemberEles[i];
                    const currentName = currentMemberEle.querySelector('.c-member_name').innerText;
                    const currentMemberId = currentMemberEle.id;
                    if (namesMap[currentMemberId] != undefined) {
                        continue
                    } else {
                        namesMap[currentMemberId] = currentName;
                    }
                } catch {
                }
            }
            await new Promise((resolve, _) => {
                setTimeout(() => {
                    resolve(true);
                }, 200);
            });
        }
        return namesMap;
    ''')
    return users

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
channelName = 'development'
browser.get("https://app.slack.com/client/TK8V2RL7Q/C01G7CFNA8K")

time.sleep(10)

log('Starting the script now')

#browser.execute_script(f'navigateToChannel("{channelName}")')
navigateToChannel(browser, channelName)
log(f'Navigation to channel {channelName} completed')

time.sleep(10)

log('Opening member list')
openMemberListForCurrentChannel(browser)
time.sleep(10)
numberOfUsers = getNumberOfUsers(browser)
log(f'Getting names of {numberOfUsers} users...')
users = getUserNames(browser)
print(users)
print(len(users))
