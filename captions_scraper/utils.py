import re

from selenium.webdriver import FirefoxOptions, Firefox, ChromeOptions, Chrome
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from captions_scraper.const import get_username, get_password, NTULEARN_URL


def init_driver(headless=True, browser="chrome"):
    if browser.lower() == "firefox":
        options = FirefoxOptions()
        service = FirefoxService(GeckoDriverManager().install())

    elif browser.lower() == "chrome":
        options = ChromeOptions()
        service = ChromeService(ChromeDriverManager().install())

    if headless:
        options.headless = True
    else:
        options.headless = False

    # disable console logging
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--log-level=3")

    if browser.lower() == "firefox":
        driver = Firefox(service=service, options=options)
    elif browser.lower() == "chrome":
        driver = Chrome(service=service, options=options)

    # keep browser open
    options.add_experimental_option("detach", True)

    driver.set_page_load_timeout(60)
    driver.implicitly_wait(1)
    driver.maximize_window()
    return driver


def login(driver):
    usernameInput = get_username()
    passwordInput = get_password()

    driver.get(NTULEARN_URL)

    username = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//input[@id='userNameInput']"))
    )
    password = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//input[@id='passwordInput']"))
    )
    login = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.XPATH, "//span[@onclick='return Login.submitLoginRequest();']")
        )
    )

    username.send_keys(usernameInput)
    password.send_keys(passwordInput)

    login.click()


def is_on_login_page(driver):
    try:
        driver.find_element(
            By.XPATH, "//span[@onclick='return Login.submitLoginRequest();']"
        )
    except NoSuchElementException:
        return False
    return True


def is_page_not_found(driver):
    try:
        driver.find_element(By.XPATH, "//div[@id='bbNG.receiptTag.content']")
    except NoSuchElementException:
        return False
    return True


def scrape_captions(url, driver):
    # load NTUlearn link containing kaltura video
    driver.get(url)

    # re-login on session timeout
    if is_page_not_found(driver) or is_on_login_page(driver):
        login(driver)
        driver.get(url)

    course_title = driver.find_element(
        By.XPATH, "//span[@ng-if='::!panelHeaderTitleTranslateKey']"
    )

    video_title = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//h1[@analytics-id='components.directives.content.panelHeader.secondaryTitle.header']",
            )
        )
    )

    title = (
        get_valid_file_name(course_title.get_attribute("innerText"))
        + "_"
        + get_valid_file_name(video_title.text)
    )

    try:
        # switch to video player container iframe
        WebDriverWait(driver, 30).until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.XPATH, "//iframe[@title='Embedded Content iFrame']")
            )
        )
        # switch to video player iframe
        WebDriverWait(driver, 30).until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.XPATH, "//iframe[@id='kplayer_ifp']")
            )
        )
        track = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//track[@kind='subtitles']"))
        )
        captions_url = track.get_attribute("src")
    except:
        print("Unable to get video captions")

    # load captions text file
    driver.get(captions_url)

    captions = driver.find_element(By.XPATH, "//pre").text
    return captions, title


def get_valid_file_name(file_name):
    # remove characters that are not alphanumeric or in [._-]
    file_name = re.sub(r"[^\w._-]", "_", file_name)
    # remove repeated dashes and strip trailing dashes
    file_name = re.sub(r"[_-]+", "-", file_name).strip("_-")
    return file_name


def parse_captions(captions):
    captions_list = captions.splitlines()
    clean_text_list = []
    for line in captions_list:
        # remove caption line number ^\d+$
        # remove timestamp ^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$
        # remove newline ^\n$
        # remove empty string ^$
        if re.match(
            "^\d+$|^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$|^\n$|^$", line
        ):
            continue
        # remove newline at end of line
        line = re.sub(r"\n", "", line)
        clean_text_list.append(line)
    clean_text = " ".join(clean_text_list)
    return clean_text
