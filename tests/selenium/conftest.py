import os
import time
import uuid

import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


API_BASE = os.getenv("TASKFLOW_API_URL", "http://127.0.0.1:8000")
UI_BASE = os.getenv("TASKFLOW_UI_URL", "http://127.0.0.1:5173")
DEFAULT_PASSWORD = os.getenv("TASKFLOW_TEST_PASSWORD", "Password123!")
# Overall wait budget for slower operations (can be overridden via env)
WAIT_SECONDS = int(os.getenv("TASKFLOW_WAIT_SECONDS", "8"))
# Shorter wait for UI interactions and element polling
SHORT_WAIT = int(os.getenv("TASKFLOW_SHORT_WAIT", "3"))

OWNER = {
    "name": "Selenium Owner",
    "email": "selenium.owner.taskflow@example.com",
    "password": DEFAULT_PASSWORD,
    "role": "member",
}
MEMBER = {
    "name": "Selenium Member",
    "email": "selenium.member.taskflow@example.com",
    "password": DEFAULT_PASSWORD,
    "role": "member",
}
OUTSIDER = {
    "name": "Selenium Outsider",
    "email": "selenium.outsider.taskflow@example.com",
    "password": DEFAULT_PASSWORD,
    "role": "member",
}


def wait_for_api(session: requests.Session):
    deadline = time.time() + WAIT_SECONDS
    while time.time() < deadline:
        try:
            response = session.get(f"{API_BASE}/", timeout=2)
            if response.ok:
                return
        except requests.RequestException:
            pass
        time.sleep(0.5)
    raise RuntimeError(f"TaskFlow API is not reachable at {API_BASE}")


def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def ensure_user(session: requests.Session, user: dict):
    response = session.post(
        f"{API_BASE}/users/",
        json={
            "name": user["name"],
            "email": user["email"],
            "password": user["password"],
            "role": user.get("role", "member"),
        },
        timeout=10,
    )
    if response.status_code not in (200, 400):
        response.raise_for_status()


def login_api(session: requests.Session, email: str, password: str):
    response = session.post(
        f"{API_BASE}/login",
        json={"email": email, "password": password},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def get_users(session: requests.Session, token: str):
    response = session.get(f"{API_BASE}/users/", headers=auth_headers(token), timeout=10)
    response.raise_for_status()
    return response.json()


def get_user_id(session: requests.Session, token: str, email: str):
    users = get_users(session, token)
    for user in users:
        if user["email"] == email:
            return user["id"]
    raise RuntimeError(f"User not found: {email}")


def create_project_api(session: requests.Session, token: str, name: str, description: str = "Selenium project"):
    response = session.post(
        f"{API_BASE}/projects/",
        headers={**auth_headers(token), "Content-Type": "application/json"},
        json={"name": name, "description": description, "members": []},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def create_task_api(
    session: requests.Session,
    token: str,
    project_id: int,
    name: str,
    description: str = "Selenium task",
    assigned_to=None,
    status: str = "to-do",
):
    response = session.post(
        f"{API_BASE}/tasks/",
        headers={**auth_headers(token), "Content-Type": "application/json"},
        json={
            "name": name,
            "description": description,
            "project_id": project_id,
            "assigned_to": assigned_to,
            "status": status,
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


@pytest.fixture(scope="session")
def api_session():
    session = requests.Session()
    wait_for_api(session)
    ensure_user(session, OWNER)
    ensure_user(session, MEMBER)
    ensure_user(session, OUTSIDER)

    owner_token = login_api(session, OWNER["email"], OWNER["password"])
    member_token = login_api(session, MEMBER["email"], MEMBER["password"])
    outsider_token = login_api(session, OUTSIDER["email"], OUTSIDER["password"])

    return {
        "session": session,
        "owner_token": owner_token,
        "member_token": member_token,
        "outsider_token": outsider_token,
        "owner_id": get_user_id(session, owner_token, OWNER["email"]),
        "member_id": get_user_id(session, owner_token, MEMBER["email"]),
        "outsider_id": get_user_id(session, owner_token, OUTSIDER["email"]),
        "owner": OWNER,
        "member": MEMBER,
        "outsider": OUTSIDER,
    }


@pytest.fixture(scope="session")
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1440,1400")

    chrome_binary = os.getenv("CHROME_BINARY", "/usr/bin/google-chrome")
    if os.path.exists(chrome_binary):
        options.binary_location = chrome_binary

    browser = webdriver.Chrome(options=options)
    browser.set_page_load_timeout(WAIT_SECONDS)
    yield browser
    browser.quit()


@pytest.fixture(autouse=True)
def reset_browser(driver):
    driver.get(UI_BASE)
    driver.delete_all_cookies()
    driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
    driver.get(UI_BASE)
    WebDriverWait(driver, SHORT_WAIT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="login-page"]'))
    )


@pytest.fixture
def seeded_project(api_session):
    name = f"Selenium Project {uuid.uuid4().hex[:8]}"
    project = create_project_api(
        api_session["session"],
        api_session["owner_token"],
        name=name,
        description="Project used by Selenium tests",
    )
    return project


@pytest.fixture
def seeded_project_with_member(api_session):
    project = create_project_api(
        api_session["session"],
        api_session["owner_token"],
        name=f"Selenium Team {uuid.uuid4().hex[:8]}",
        description="Project with a member",
    )
    response = api_session["session"].post(
        f"{API_BASE}/projects/{project['id']}/members/{api_session['member_id']}",
        headers=auth_headers(api_session["owner_token"]),
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


@pytest.fixture
def seeded_task(api_session, seeded_project_with_member):
    task = create_task_api(
        api_session["session"],
        api_session["owner_token"],
        project_id=seeded_project_with_member["id"],
        name=f"Selenium Task {uuid.uuid4().hex[:8]}",
        description="Task used for Selenium tests",
        assigned_to=api_session["member_id"],
    )
    return seeded_project_with_member, task


def wait_for_element(driver, css_selector: str):
    return WebDriverWait(driver, WAIT_SECONDS).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
    )


def wait_for_visible(driver, css_selector: str):
    return WebDriverWait(driver, SHORT_WAIT).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector))
    )


def set_auth_token(driver, token: str):
    driver.get(UI_BASE)
    driver.execute_script("window.localStorage.setItem('token', arguments[0]);", token)


def open_dashboard(driver, token: str):
    set_auth_token(driver, token)
    driver.get(f"{UI_BASE}/dashboard")
    wait_for_element(driver, '[data-testid="dashboard-page"]')


def open_project(driver, token: str, project_id: int):
    set_auth_token(driver, token)
    driver.get(f"{UI_BASE}/project/{project_id}")
    wait_for_element(driver, '[data-testid="project-detail-page"]')


def safe_select_dropdown(driver, select_selector: str, option_text: str = None, option_value: str = None, max_retries: int = 3):
    """
    Safely select from a dropdown with retry logic to handle async option loading.
    
    This handles race conditions where the dropdown options haven't finished loading
    when the Select element is created.
    
    Args:
        driver: Selenium WebDriver
        select_selector: CSS selector for the select element
        option_text: Exact visible text of the option to select (mutually exclusive with option_value)
        option_value: Value attribute of the option to select (mutually exclusive with option_text)
        max_retries: Number of retries if selection fails
    """
    from selenium.webdriver.support.ui import Select
    
    if option_text is None and option_value is None:
        raise ValueError("Must provide either option_text or option_value")
    
    for attempt in range(max_retries):
        try:
            # Wait for select to be visible
            select_element = wait_for_visible(driver, select_selector)
            
            # Click to open dropdown and trigger option loading
            select_element.click()
            time.sleep(0.15)  # very brief pause for dropdown to render

            # Wait for options to be present in DOM (short wait)
            WebDriverWait(driver, SHORT_WAIT).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, f'{select_selector} option')) > 1
            )
            
            # Create Select and select by provided method
            select = Select(select_element)
            if option_text:
                select.select_by_visible_text(option_text)
            else:
                select.select_by_value(option_value)
            return  # Success
        except Exception as e:
            if attempt == max_retries - 1:
                raise  # Last attempt, re-raise the exception
            time.sleep(0.25)  # shorter wait before retry
