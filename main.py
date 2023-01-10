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
        print("Failed to login")
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


def main():
    driver = init_driver(True, "chrome")
    get_captions(driver)


if __name__ == "__main__":
    main()
