import uuid

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .conftest import UI_BASE, open_dashboard, open_project, wait_for_element, wait_for_visible, safe_select_dropdown


def fill(driver, selector: str, value: str):
    element = wait_for_visible(driver, selector)
    element.clear()
    element.send_keys(value)


def click(driver, selector: str):
    wait_for_visible(driver, selector).click()


def text(driver, selector: str):
    return wait_for_visible(driver, selector).text


def test_login_page_renders(driver):
    assert wait_for_visible(driver, '[data-testid="login-page"]')
    assert text(driver, 'h1') == "TaskFlow"
    assert wait_for_visible(driver, '[data-testid="login-tab-button"]')
    assert wait_for_visible(driver, '[data-testid="signup-tab-button"]')


def test_signup_tab_reveals_name_field(driver):
    click(driver, '[data-testid="signup-tab-button"]')
    assert wait_for_visible(driver, '[data-testid="name-input"]')
    assert text(driver, '[data-testid="auth-submit-button"]') == "Sign Up"


def test_signup_flow_creates_account(driver):
    click(driver, '[data-testid="signup-tab-button"]')
    email = f"signup.{uuid.uuid4().hex[:8]}@example.com"
    fill(driver, '[data-testid="name-input"]', "Selenium Signup User")
    fill(driver, '[data-testid="email-input"]', email)
    fill(driver, '[data-testid="password-input"]', "Password123!")
    click(driver, '[data-testid="auth-submit-button"]')
    message = text(driver, '[data-testid="auth-message"]')
    assert "Account created! Please login." in message
    assert text(driver, '[data-testid="auth-submit-button"]') == "Login"


def test_invalid_login_shows_error(driver):
    fill(driver, '[data-testid="email-input"]', f"missing.{uuid.uuid4().hex[:8]}@example.com")
    fill(driver, '[data-testid="password-input"]', "bad-password")
    click(driver, '[data-testid="auth-submit-button"]')
    assert "Login failed" in text(driver, '[data-testid="auth-message"]')


def test_valid_login_redirects_to_dashboard(driver, api_session):
    fill(driver, '[data-testid="email-input"]', api_session["owner"]["email"])
    fill(driver, '[data-testid="password-input"]', api_session["owner"]["password"])
    click(driver, '[data-testid="auth-submit-button"]')
    wait_for_element(driver, '[data-testid="dashboard-page"]')
    assert text(driver, '[data-testid="projects-heading"]') == "Projects"


def test_dashboard_redirects_without_token(driver):
    driver.get(f"{UI_BASE}/dashboard")
    wait_for_element(driver, '[data-testid="login-page"]')
    assert text(driver, 'h1') == "TaskFlow"


def test_dashboard_logout_returns_to_login(driver, api_session):
    open_dashboard(driver, api_session["owner_token"])
    click(driver, '[data-testid="logout-button"]')
    wait_for_element(driver, '[data-testid="login-page"]')


def test_dashboard_new_project_form_opens(driver, api_session):
    open_dashboard(driver, api_session["owner_token"])
    click(driver, '[data-testid="new-project-button"]')
    assert wait_for_visible(driver, '[data-testid="project-form"]')
    assert wait_for_visible(driver, '[data-testid="project-name-input"]')


def test_create_project_from_dashboard(driver, api_session):
    open_dashboard(driver, api_session["owner_token"])
    click(driver, '[data-testid="new-project-button"]')
    project_name = f"Browser Project {uuid.uuid4().hex[:8]}"
    fill(driver, '[data-testid="project-name-input"]', project_name)
    fill(driver, '[data-testid="project-description-input"]', "Created through the UI")
    click(driver, '[data-testid="project-create-button"]')
    wait_for_element(driver, '[data-testid="dashboard-page"]')
    assert project_name in wait_for_visible(driver, '[data-testid="project-list"]').text


def test_project_card_opens_detail_page(driver, api_session, seeded_project):
    open_dashboard(driver, api_session["owner_token"])
    wait_for_visible(driver, f'[data-testid="project-card-{seeded_project["id"]}"]').click()
    wait_for_element(driver, '[data-testid="project-detail-page"]')
    assert seeded_project["name"] in text(driver, 'h1')


def test_project_detail_shows_members_section(driver, api_session, seeded_project_with_member):
    open_project(driver, api_session["owner_token"], seeded_project_with_member["id"])
    assert wait_for_visible(driver, '[data-testid="members-section"]')
    assert "Team Members" in text(driver, '[data-testid="members-section"]')
    assert "Owner" in text(driver, '[data-testid="members-section"]')


def test_owner_can_open_add_member_form(driver, api_session, seeded_project_with_member):
    open_project(driver, api_session["owner_token"], seeded_project_with_member["id"])
    click(driver, '[data-testid="add-member-button"]')
    assert wait_for_visible(driver, '[data-testid="add-member-form"]')
    assert wait_for_visible(driver, '[data-testid="member-select"]')


def test_owner_can_add_member_to_project(driver, api_session, seeded_project):
    open_project(driver, api_session["owner_token"], seeded_project["id"])
    click(driver, '[data-testid="add-member-button"]')
    
    # Use safe dropdown selection with retry logic to handle async option loading
    safe_select_dropdown(
        driver,
        '[data-testid="member-select"]',
        f'{api_session["member"]["name"]} ({api_session["member"]["email"]})'
    )
    
    click(driver, '[data-testid="member-submit-button"]')
    wait_for_visible(driver, '[data-testid="members-section"]')
    members_text = text(driver, '[data-testid="members-section"]')
    assert api_session["member"]["email"] in members_text


def test_owner_can_open_add_task_form(driver, api_session, seeded_project_with_member):
    open_project(driver, api_session["owner_token"], seeded_project_with_member["id"])
    click(driver, '[data-testid="add-task-button"]')
    assert wait_for_visible(driver, '[data-testid="task-form"]')
    assert wait_for_visible(driver, '[data-testid="task-name-input"]')


def test_owner_can_create_task(driver, api_session, seeded_project_with_member):
    open_project(driver, api_session["owner_token"], seeded_project_with_member["id"])
    click(driver, '[data-testid="add-task-button"]')
    task_name = f"UI Task {uuid.uuid4().hex[:8]}"
    fill(driver, '[data-testid="task-name-input"]', task_name)
    fill(driver, '[data-testid="task-description-input"]', "Created from Selenium")
    
    # Use safe dropdown selection with retry logic
    safe_select_dropdown(
        driver,
        '[data-testid="task-assignee-select"]',
        option_text=api_session["member"]["name"]
    )
    
    click(driver, '[data-testid="task-create-button"]')
    wait_for_visible(driver, '[data-testid="todo-column"]')
    assert task_name in text(driver, '[data-testid="todo-column"]')


def test_owner_can_move_task_to_in_progress(driver, api_session, seeded_task):
    project, task = seeded_task
    open_project(driver, api_session["owner_token"], project["id"])
    task_card = wait_for_visible(driver, f'[data-testid="task-card-{task["id"]}"]')
    
    # Use safe dropdown selection with value-based selection
    status_select_selector = f'[data-testid="task-card-{task["id"]}"] [data-testid="task-status-select"]'
    safe_select_dropdown(
        driver,
        status_select_selector,
        option_value="in-progress"
    )
    
    wait_for_visible(driver, '[data-testid="in-progress-column"]')
    assert task["name"] in text(driver, '[data-testid="in-progress-column"]')


def test_owner_can_delete_task(driver, api_session, seeded_task):
    project, task = seeded_task
    open_project(driver, api_session["owner_token"], project["id"])
    task_card = wait_for_visible(driver, f'[data-testid="task-card-{task["id"]}"]')
    task_card.find_element(By.CSS_SELECTOR, '[data-testid="task-delete-button"]').click()
    driver.switch_to.alert.accept()
    
    # Wait for the task card to disappear from the page
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, f'[data-testid="task-card-{task["id"]}"]'))
    )
