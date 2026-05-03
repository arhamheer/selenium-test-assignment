import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

API='http://127.0.0.1:9000'
UI='http://127.0.0.1:5173'
owner_email='selenium.owner.taskflow@example.com'
owner_pass='Password123!'

# get token
r=requests.post(f"{API}/login", json={'email': owner_email, 'password': owner_pass})
print('login status', r.status_code)
if r.status_code!=200:
    print(r.text)
    raise SystemExit(1)
token=r.json()['access_token']
print('token len', len(token))

opts=Options()
opts.add_argument('--headless=new')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--window-size=1200,800')
from selenium.webdriver.common.by import By

browser=webdriver.Chrome(options=opts)
try:
    browser.get(UI)
    browser.execute_script("window.localStorage.setItem('token', arguments[0]);", token)
    browser.get(UI + '/dashboard')
    time.sleep(2)
    print('current url:', browser.current_url)
    print('page title:', browser.title)
    src=browser.page_source
    print('--- PAGE SOURCE START ---')
    print(src[:8000])
    print('--- PAGE SOURCE END ---')
    try:
        el=browser.find_element(By.CSS_SELECTOR,'[data-testid="dashboard-page"]')
        print('Found dashboard element')
    except Exception as e:
        print('Dashboard element not found:', e)
finally:
    browser.quit()
