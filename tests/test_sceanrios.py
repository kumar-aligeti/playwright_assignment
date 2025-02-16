import json
import os
import urllib
import subprocess
import pytest
from playwright.sync_api import sync_playwright

LAMBDATEST_USERNAME = "kumaraswamy.nitk"
LAMBDATEST_ACCESS_KEY = "LT_SPql2Gxrv692PXwB8HcGsEo7jfjyxi8q58KsI1JxaeiLbjh"

# Define the common capabilities function based on browser type
def get_capabilities(browser_name):
    capabilities = {
        'browserName': browser_name,  # Browser name (Chrome or MicrosoftEdge)
        'browserVersion': 'latest',
        'LT:Options': {
            'platform': 'Windows 10',  # You can modify the platform as needed
            'build': 'Playwright Python Build',
            'name': 'Playwright Test',
            'user': LAMBDATEST_USERNAME,
            'accessKey': LAMBDATEST_ACCESS_KEY,
            'project': "Untitled",
            "w3c": True,
            "plugin": "python-pytest",
            'screenshots': True,
            'network': True,
            'video': True,
            'console': True,
            'tunnel': False,  # Add tunnel configuration if testing locally hosted webpage
            'tunnelName': '',  # Optional
            'geoLocation': '',  # country code can be fetched from https://www.lambdatest.com/capabilities-generator/
        }
    }

    playwrightVersion = str(subprocess.getoutput('playwright --version')).strip().split(" ")[1]
    capabilities['LT:Options']['playwrightClientVersion'] = playwrightVersion

    return capabilities

# Parametrize the test for multiple browsers (Chrome and MicrosoftEdge)
@pytest.fixture(scope="module", params=["Chrome", "MicrosoftEdge"])
def browser(request):
    browser_name = request.param
    capabilities = get_capabilities(browser_name)

    with sync_playwright() as p:
        lt_cdp_url = 'wss://cdp.lambdatest.com/playwright?capabilities=' + urllib.parse.quote(json.dumps(capabilities))
        print(f"Connecting to LambdaTest using {browser_name} with URL: {lt_cdp_url}")
        browser = p.chromium.connect(lt_cdp_url) if browser_name == 'Chrome' else p.firefox.connect(lt_cdp_url)

        yield browser

        # Teardown: Close the browser
        browser.close()

@pytest.fixture(scope="function")
def page(browser):
    url = 'https://www.lambdatest.com/selenium-playground/'
    expected_title = 'Selenium Grid Online | Run Selenium Test On Cloud'
    page_instance = browser.new_page()
    # Navigate to the URL
    page_instance.goto(url)
    # Get the title of the page
    actual_title = page_instance.title()
    assert actual_title == expected_title

    yield page_instance
    # Teardown: Close the page
    page_instance.close()

def test_simple_form_data(page):
    # Locators
    sample_form_demo_locator_link = "//a[normalize-space()='Simple Form Demo']"
    sample_input_locator = "//input[@id='user-message']"
    get_checked_value_button_locator = "//button[@id='showInput']"
    displayed_message_locator = "//p[@id='message']"

    # variable Values
    substring = 'simple-form-demo'
    sample_input = "Welcome to LambdaTest"


    # Goto Sample Form Demo and verify substring is present
    page.locator(sample_form_demo_locator_link).click()
    current_url = page.url
    assert substring in current_url

    # Enter the value and verify value is displayed
    page.locator(sample_input_locator).fill(sample_input)
    page.locator(get_checked_value_button_locator).click()
    saved_value = page.locator(displayed_message_locator).text_content()
    assert saved_value == sample_input
    page.screenshot(path='sample_input.png')


def test_drag_and_drop_slider(page):
    # Locators
    drag_and_drop_locator_link = "//a[normalize-space()='Drag & Drop Sliders']"
    drag_and_drop_slider_locator = "//input[@value='15']"
    value_display_locator = "#rangeSuccess"

    slider = page.locator(drag_and_drop_slider_locator)
    value_display = page.locator(value_display_locator)

    # Click on Drag and drop link
    page.locator(drag_and_drop_locator_link).click()

    # Wait for the correct slider section to be visible
    page.locator("#slider3").wait_for(timeout=60000)

    # Locate the slider and output element
    slider = page.locator("#slider3 input[type='range']")
    output = page.locator("#slider3 output")

    # Get the slider's bounding box
    box = slider.bounding_box()
    assert box is not None, "❌ Slider bounding box not found!"

    # Start dragging from the left of the slider
    start_x = box["x"] + 5
    y_center = box["y"] + box["height"] / 2
    page.mouse.move(start_x, y_center)
    page.mouse.down()

    # Move the slider in smaller steps
    final_value = "15"
    for step in range(100):  # Smaller steps to prevent overshooting
        move_x = start_x + (box["width"] * (0.01 * (step + 1)))  # Move 5% each time
        page.mouse.move(move_x, y_center)
        page.wait_for_timeout(200)  # Short wait for UI update
        final_value = output.text_content().strip()
        print(f"🔄 Current slider value: {final_value}")

        if final_value == "95":
            break  # Stop exactly at 95

    page.mouse.up()

    # Wait for UI update
    page.wait_for_timeout(2000)

    # Validate if the displayed value is 95
    print(f"✅ Final slider value: {final_value}")

    assert final_value == "95", f"Test Failed! Expected 95 but got {final_value}"
    page.screenshot(path='drag_and_drop.png')


def test_input_form_submit(page):
    # Locators
    input_form_submit_locator_link = "//a[normalize-space()='Input Form Submit']"
    submit_form_button_locator = "//button[normalize-space()='Submit']"
    name_field_locator = "//input[@id='name']"
    email_field_locator = "//input[@id='inputEmail4']"
    password_field_locator = "//input[@id='inputPassword4']"
    company_field_locator = "//input[@id='company']"
    website_field_locator = "//input[@id='websitename']"
    country_field_locator = "//select[@name='country']"
    city_field_locator = "//input[@id='inputCity']"
    address1_field_locator = "//input[@id='inputAddress1']"
    address2_field_locator = "//input[@id='inputAddress2']"
    state_field_locator = "//input[@id='inputState']"
    zip_field_locator = "//input[@id='inputZip']"
    success_message_locator = "//p[@class='success-msg hidden' and contains(., 'Thanks for contacting us, we will get back to you shortly.')]"


    # Variable Values
    name = "Lamda test user"
    email = "lamdatestuser@gmail.com"
    password = "lamdaTest12345"
    company = "Software Testing"
    website = "https://www.lambdatest.com"
    country = "United States"
    city = "Austin"
    address_1 = "#21, abc street"
    address_2 = "xyz Area"
    state = "New York"
    zip_code = '123456'


    # Click on Drag and drop link
    page.locator(input_form_submit_locator_link).click()

    # Verifying Error message is Displayed
    # Click on Submit Button
    page.locator(submit_form_button_locator).click()
    # Extract validation message using JavaScript
    validation_message = page.locator("#inputLastName").evaluate("el => el.validationMessage")

    # Validate the expected message
    assert validation_message == "Please fill in this field.", f"Unexpected message: {validation_message}"
    print("✅ Validation message is correctly displayed:", validation_message)

    page.screenshot(path='error_message.png')

    # Adding data in all fields
    page.locator(name_field_locator).fill(name)
    page.locator(email_field_locator).fill(email)
    page.locator(password_field_locator).fill(password)
    page.locator(company_field_locator).fill(company)
    page.locator(website_field_locator).fill(website)
    page.locator(country_field_locator).select_option(country)
    page.locator(city_field_locator).fill(city)
    page.locator(address1_field_locator).fill(address_1)
    page.locator(address2_field_locator).fill(address_2)
    page.locator(state_field_locator).fill(state)
    page.locator(zip_field_locator).fill(zip_code)

    page.screenshot(path='user_data_before_save.png')
    # Click on Submit Button
    page.locator(submit_form_button_locator).click()

    # Verifying Success message is displayed
    page.locator(success_message_locator).scroll_into_view_if_needed()
    page.locator(success_message_locator).is_visible()
    page.screenshot(path='user_saved.png')
