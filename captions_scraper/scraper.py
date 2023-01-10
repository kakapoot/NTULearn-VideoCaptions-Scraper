import re

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from const import get_username, get_password, INPUT_FILE_PATH, OUTPUT_DIR


def init_driver():
    # TODO: support other browsers

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    driver.set_page_load_timeout(60)
    driver.maximize_window()
    return driver


def login(driver):
    usernameInput = get_username()
    passwordInput = get_password()

    driver.get("https://ntulearn.ntu.edu.sg/")
    driver.implicitly_wait(30)

    username = driver.find_element(By.XPATH, "//input[@id='userNameInput']")
    password = driver.find_element(By.XPATH, "//input[@id='passwordInput']")

    submit = driver.find_element(By.XPATH, "//span[@id='submitButton']")

    username.send_keys(usernameInput)
    password.send_keys(passwordInput)

    submit.click()


def scrape_captions(url, driver):
    # load NTUlearn link containing kaltura video
    driver.get(url)
    driver.implicitly_wait(30)

    # get valid file name
    course_title = driver.find_element(
        By.XPATH,
        "//h1[@analytics-id='components.directives.content.panelHeader.secondaryTitle.header']",
    )
    video_title = driver.find_element(
        By.XPATH, "//span[@ng-if='::!panelHeaderTitleTranslateKey']"
    )
    title = (
        get_valid_file_name(course_title.text)
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
    driver.implicitly_wait(30)

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


def main():
    driver = init_driver()
    login(driver)

    with open(INPUT_FILE_PATH) as input_file:
        urls = input_file.read().splitlines()
        for url in urls:
            # TODO: check if logged in
            captions, title = scrape_captions(url, driver)
            clean_text = parse_captions(captions)

            output_file_name = title + ".txt"
            output_file_path = OUTPUT_DIR + output_file_name
            with open(output_file_path, "w") as output_file:
                output_file.write(clean_text)


if __name__ == "__main__":
    main()
