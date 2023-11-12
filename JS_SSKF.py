import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import re

exact_keywords = ["password", "pass", "database", "DB", "username", "user", "users", "/etc", "http://", "https://",
                  "api", "token", "secret", "secrets", "db_name", "db_pass", "db_password", "api_key", "apikey",
                  "admin", "root", "ssh", "ftp", "localhost", "telnet", "sql", "mysql", "postgres", "oracle", "mssql",
                  "mongodb", "nosql", ".htaccess", "htaccess", ".env", "custom_token", "apis", "aws", "azure", "blob",
                  "s3", "smtp", "lambda", "private", "oauth", "port"]


# Function to search for exact keywords in a JS file and print lines with occurrences
def search_exact_keywords(js_url):
    try:
        js_content = requests.get(js_url).text

        # Initialize a dictionary to count occurrences for each keyword
        keyword_occurrences = {keyword: 0 for keyword in exact_keywords}

        for keyword in exact_keywords:
            # Search for the exact keyword with word boundaries using regular expressions
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = re.finditer(pattern, js_content, re.IGNORECASE)

            # Count occurrences and store in the dictionary
            keyword_occurrences[keyword] = len(list(matches))

        # Print keywords with non-zero occurrences
        non_zero_keywords = {keyword: occurrences for keyword, occurrences in keyword_occurrences.items() if
                             occurrences > 0}
        if non_zero_keywords:
            print(f"Total occurrences in {js_url}:")
            for keyword, occurrences in non_zero_keywords.items():
                print(f"{keyword}: {occurrences}")

    except requests.exceptions.RequestException as e:
        print(f"Error while processing {js_url}: {e}")
    except Exception as e:
        print(f"An error occurred while processing {js_url}: {e}")


def extract_js_urls(url, js_urls):
    try:
        response = requests.get(url)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all script tags
        script_tags = soup.find_all("script")

        for script in script_tags:
            src = script.get("src")
            if src:
                # Construct the absolute URL for the JS file
                js_url = urljoin(url, src)

                # Add the JS file URL to the set to ensure uniqueness
                js_urls.add(js_url)
    except requests.exceptions.RequestException as e:
        print(f"Error while extracting JS files from {url}: {e}")
    except Exception as e:
        print(f"An error occurred while extracting JS files from {url}: {e}")


# Process each URL and extract JS file URLs
def start():
    with open('extracted_urls.txt', 'r') as file:
        urls = [line.strip() for line in file]

    js_urls = set()
    for url in urls:
        extract_js_urls(url, js_urls)

    # Save unique JS file URLs to a text file
    with open('js_urls.txt', 'w') as file:
        for js_url in js_urls:
            file.write(js_url + '\n')
            search_exact_keywords(js_url)
    print("js Files extraction completed")


def crawler(base_url):
    url = base_url
    unique_urls = set()

    try:
        response = requests.get(url)
        # print(response.text, response.status_code)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            href_tags = soup.find_all('a', href=True)
            with open('extracted_urls.txt', 'w') as file:
                for tag in href_tags:
                    href = tag['href']
                    complete_url = urljoin(url, href)
                    if complete_url.startswith(base_url):
                        unique_urls.add(complete_url)

                for unique_url in unique_urls:
                    file.write(unique_url + '\n')
        else:
            print(f"Failed to retrieve the web page. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred with the URL: {e}")


if __name__ == "__main__":
    base_url = input("Enter your URL with https: \n")
    if os.path.exists('extracted_urls.txt'):
        os.remove('extracted_urls.txt')
    if os.path.exists('js_files.txt'):
        os.remove('js_files.txt')
    crawler(base_url)
    if os.path.getsize("extracted_urls.txt") != 0:
        start()
