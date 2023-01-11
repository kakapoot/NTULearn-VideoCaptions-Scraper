import argparse

from captions_scraper.const import INPUT_FILE_PATH, OUTPUT_DIR
from captions_scraper.utils import (
    init_driver,
    login,
    scrape_captions,
    parse_captions,
    is_on_login_page,
)


def get_captions(driver):
    print("Logging in...")
    login(driver)

    if is_on_login_page(driver):
        print(
            "Failed to login. Check if correct NTULearn login details have been entered in .env file"
        )
        return

    else:
        print("Login successful")

    with open(INPUT_FILE_PATH) as input_file:
        urls = input_file.read().splitlines()
        for url in urls:
            print("Getting captions at " + url)
            captions, title = scrape_captions(url, driver)
            clean_text = parse_captions(captions)

            output_file_name = title + ".txt"
            output_file_path = OUTPUT_DIR + output_file_name
            with open(output_file_path, "w") as output_file:
                output_file.write(clean_text)
                print("Saved to output directory: " + output_file_name)

    print("Finished getting all captions")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape captions of NTULearn videos")

    parser.add_argument(
        "--firefox", action="store_true", help="Use Firefox instead of Chrome"
    )
    parser.add_argument(
        "--no_headless",
        action="store_false",
        help="Show UI, do not use web browser in headless mode",
    )
    args = parser.parse_args()

    firefox = args.firefox
    headless = args.no_headless

    driver = init_driver(headless=headless, firefox=firefox)
    get_captions(driver)
