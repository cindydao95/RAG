import sqlite3
import ssl
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime

#filename: cd ~/desktop/web_scrapping && python3 openbing_tess.py

# Ignore SSL certificate errors
ssl._create_default_https_context = ssl._create_unverified_context

# Set up the SQLite database
conn = sqlite3.connect('tessdouglas.sqlite')
cur = conn.cursor()

# Create the URL table if it doesn't exist
cur.execute('''
CREATE TABLE IF NOT EXISTS Bing (
    id INTEGER PRIMARY KEY,
    url TEXT UNIQUE,
    retrieved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    copies_id integer
)
''')

def _get_edge_options():
    edge_options = webdriver.EdgeOptions()
    edge_options.add_argument("--enable-chrome-browser-cloud-management")
    edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    edge_options.add_experimental_option('detach', True)
    #edge_options.add_argument('--headless')
    edge_options.add_argument("-width=1920")
    edge_options.add_argument("-height=1080")
    return edge_options

def extract_bing_urls(driver, search_query, max_links):
    driver.get("https://www.bing.com")
    # Perform search
    element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.NAME, "q")))
    element.click()
    element.send_keys(search_query)
    element.send_keys(Keys.ENTER)

    unique_bing = set()
    links_retrieved = 0

    while links_retrieved < max_links:
        # Wait for results to load
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, "//li[@class='b_algo']//h2/a")))
        elems = driver.find_elements(By.XPATH, "//a[contains(.//strong, 'Tess Douglas') and (contains(text(), '’s Post - LinkedIn') or contains(text(), 'on LinkedIn'))]")

        for e in elems:
            link = e.get_attribute('href')
            # Check if the href attribute is not empty or not already in the set
            if link and link not in unique_bing:
                unique_bing.add(link)
                links_retrieved += 1
                conn.commit()
                try:
                    # Get the current time in UTC
                    utc_now = datetime.datetime.now()
                    retrieve_at=utc_now.strftime("%c")
                    # Convert the current time to Chicago time
                    cur.execute('INSERT OR IGNORE INTO Bing (url, retrieved_at) VALUES (?, ?)', (link, retrieve_at))
                    conn.commit()
                except sqlite3.Error as e:
                    conn.commit()
                if links_retrieved >= max_links:
                    break

        if links_retrieved >= max_links:
            break

        # Click the next page button
        try:
            next_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//a[@title='Next page']")))
            next_button.click()
            time.sleep(2)  # Give some time for the next page to load
            conn.commit()
        except Exception as e:
            print(f'Exception: {str(e)}')
        except:
            print("No more pages available or unable to find the next button.")
            break

    conn.commit()

# Prompt the user for the number of links to retrieve
max_links = int(input("How many links do you want to retrieve? "))

# Example usage
edge_options = _get_edge_options()
driver = webdriver.Edge(options=edge_options)

try:
    extract_bing_urls(driver, "Tess Douglas site:linkedin.com", max_links)
finally:
    driver.quit()
    cur.close()
    conn.commit()
    conn.close()
