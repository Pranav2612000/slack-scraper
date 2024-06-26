import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
import json

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

def getInnerText(browser, element):
    return browser.execute_script("return arguments[0].innerText", element)


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

def searchForUser(browser, username):
    log(f'searching for {username}')
    try:
        clearSearchBtn = browser.find_element(By.XPATH, '//button[@data-qa="close_input"]')
        clearSearchBtn.click()
    except Exception as e:
        pass

    searchInput = browser.find_element(By.XPATH, '//input[@data-qa="members_dialog_filter_input"]')
    searchInput.send_keys(username)

def getUserNameAndDisplayName(browser, userId):
    userProfile = browser.find_element(By.ID, userId)
    try:
        name = getInnerText(browser, userProfile.find_element(By.CLASS_NAME, 'c-member_name'))
    except:
        name = ''

    try:
        displayName = getInnerText(browser, userProfile.find_element(By.CLASS_NAME, 'c-member__secondary-name'))
    except:
        displayName = ''

    return { 'name': name, 'displayName': displayName }

def openUserProfile(browser, userId):
    userProfile = browser.find_element(By.ID, userId)
    userProfileBtn = userProfile.find_element(By.TAG_NAME, 'button')
    userProfile.click()

def getUserData(browser):
    wait = WebDriverWait(browser, 10)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'p-flexpane__body')))

    userData = browser.execute_script('''
        const profileEle = document.querySelector('.p-flexpane__body');

        let title;
        try {
            title = profileEle.querySelector('.p-r_member_profile__subtitle').innerText;
        } catch {
            title = '';
        }

        let pronouns = '';
        try {
            const subtext = profileEle.querySelectorAll('.p-r_member_profile_section_content')[0]
                .querySelector('.break_word').innerText;
            pronouns = subtext.split('·')[0];
        } catch {
            pronouns = '';
        }

        let time;
        try {
            time = profileEle.querySelector('.p-local_time').innerText;
        } catch {
            time = '';
        }

        let status;
        try {
            status = profileEle.querySelector('.padding_left_50').innerText;
        } catch {
            status = '';
        }

        let email = '', phone = '';
        try {
            const contactDetailsEle = profileEle.querySelectorAll('.p-rimeto_member_profile_field__contact_info');
            const contactDetails = Array.from(contactDetailsEle).map(ele => ele.innerText);
            contactDetails.forEach((contactDetail) => {
                const field = contactDetail.split('\\n')[0];
                if (field.includes('Email')) {
                    email = contactDetail.split('\\n')[1];
                } else if (field.includes('Phone')) {
                    phone = contactDetail.split('\\n')[1];
                }
            });
        } catch (err) {
            email = '';
            phone = '';
        }

        let publicEmail = '', mastodon = '';
        try {
            const profileDetailsEle = profileEle.querySelectorAll('.p-rimeto_member_profile_field');
            const profileDetails = Array.from(profileDetailsEle).map(ele => ele.innerText);
            profileDetails.forEach((profileDetail) => {
                const field = profileDetail.split('\\n')[0];
                if (field.includes('Public Email')) {
                    publicEmail= profileDetail.split('\\n')[1];
                } else if (field.includes('Mastodon')) {
                    mastodon = profileDetail.split('\\n')[1];
                }
            });
        } catch (err) {
            publicEmail = '';
            mastodon = '';
        }

        return {
            title: title,
            pronouns: pronouns,
            time: time,
            email: email,
            phone: phone,
            status: status,
            publicEmail: publicEmail,
            mastodon: mastodon
        }
    ''')
    return userData

try:
    with open('cookies.json', 'r') as file:
        cookies = json.load(file)
except:
    log('Unable to get cookies')
    cookies = {}

options = ChromeOptions()
options.set_capability("timeouts", {"script": 300000 })
browser = webdriver.Chrome(options=options)
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

usersData = []
for userId in users:
    try:
        log(f'Fetching data for user {userId}')
        searchForUser(browser, users[userId])
        time.sleep(2)
        nameData = getUserNameAndDisplayName(browser, userId)
        openUserProfile(browser, userId)
        time.sleep(1)
        userMetaData = getUserData(browser)
        log('User MetaData: ')
        log(userMetaData)
        userData = {
            'name': nameData['name'],
            'displayName': nameData['displayName'],
            'title': userMetaData['title'],
            'pronouns': userMetaData['pronouns'],
            'time': userMetaData['time'],
            'email': userMetaData['email'],
            'phone': userMetaData['phone'],
            'status': userMetaData['status'],
            'mastodon': userMetaData['mastodon'],
            'publicEmail': userMetaData['publicEmail']
        }
        log(userData)
        usersData.append(userData)

        navigateToChannel(browser, channelName)
        time.sleep(5)
        openMemberListForCurrentChannel(browser)
        time.sleep(5)
    except Exception as e:
        log(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
        log(f'Could not fetch data for {userId}')
time.sleep(10)
df = pd.DataFrame(usersData)
df.to_csv("members.csv", index=False)
