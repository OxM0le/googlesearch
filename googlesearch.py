#!/bin/python3

import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import logging
import os
import datetime

def solve_captcha(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        image_data = BytesIO(response.content)
        captcha_image = Image.open(image_data)
        captcha_image.show()  # Display the CAPTCHA image for the user to solve
        captcha_solution = input("Enter the CAPTCHA solution: ")
        return captcha_solution
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve CAPTCHA image: {e}")
        print(f"Failed to retrieve CAPTCHA image: {e}")
        return None

def google_search(query, num_pages=5):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Create a directory for logs based on the search term
        log_directory = os.path.join("logs", query)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        # Log file with timestamp
        log_file = f"google_search_{query}_{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}.log"
        log_path = os.path.join(log_directory, log_file)

        logging.basicConfig(filename=log_path, level=logging.INFO,
                            format='%(message)s')

        for page in range(num_pages):
            start_index = page * 10  # Each page typically shows 10 results
            search_url = f"https://www.google.com/search?q={query}&start={start_index}"

            response = requests.get(search_url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            results = soup.find_all("div", class_="tF2Cxc")

            print(f"Page {page + 1} Results:")
            for result in results:
                title = result.find("h3").get_text()
                link = result.find("a")["href"]
                log_message = f"Title: {title}\nLink: {link}\n"
                logging.info(log_message)
                print(log_message)

            # Check for and solve CAPTCHA
            captcha_image = soup.find("img", {"alt": "CAPTCHA"})
            if captcha_image:
                captcha_image_url = captcha_image["src"]
                captcha_solution = solve_captcha(f"https://www.google.com{captcha_image_url}")
                if captcha_solution:
                    logging.info(f"Solved CAPTCHA: {captcha_solution}")
                else:
                    logging.warning("CAPTCHA solution not provided. Exiting.")
                    break
            else:
                logging.info("No CAPTCHA found on this page.")

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve search results: {e}")
        print(f"Failed to retrieve search results: {e}")
    except Exception as ex:
        logging.error(f"An error occurred: {ex}")

def main():
    try:
        search_query = input("Enter your search query: ")
        num_pages = int(input("Enter the number of pages to scrape: "))
        google_search(search_query, num_pages)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()

