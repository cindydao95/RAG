from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import sqlite3
from datetime import timedelta
import re
import datetime
import time

#filename: cd ~/desktop/web_scrapping && python3 final_robert.py

conn = sqlite3.connect('robertwebber.sqlite')
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

cur.execute('''
create table if not exists Content (
    id integer primary key,
    copies text unique,
    post_date integer
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

# Initialize WebDriver
edge_options = _get_edge_options()
driver = webdriver.Edge(options=edge_options)

cur.execute('SELECT id, url, retrieved_at FROM Bing')
bings = dict()
for bing_row in cur :
    bings[bing_row[0]] = (bing_row[1],bing_row[2])

# bings(id: url, retrieved at)

print("Loaded bings=",len(bings))

url_list=list()
for (bing_id, bing) in list(bings.items()):
    url=bing[0]
    url_list.append(url)

def take_screenshot(driver, filename):
    try:
        driver.save_screenshot(filename)
        print(f"Screenshot saved: {filename}")
    except Exception as e:
        print(f"Failed to take screenshot: {str(e)}")

def convert_relative_date(relative_date):
                        now = datetime.datetime.now()
                        match = re.match(r"(\d+)([dwmy])", relative_date)
                        if not match:
                            return None
                        value, unit = int(match.group(1)), match.group(2)
                        if unit == "h":
                            return now - timedelta(hours=value)
                        if unit == "d":
                            return now - timedelta(days=value)
                        elif unit == "w":
                            return now - timedelta(weeks=value)
                        elif unit == "m":
                            return now - timedelta(days=value*30)  # Approximation
                        elif unit == "y":
                            return now - timedelta(days=value*365)  # Approximation
                        return None

def scrape_and_get_copies(driver, list_to_read):
    count = 0
    url_count=0
    for link in list_to_read:
        url_count = url_count + 1
        #print('Url:', url_count)
        if link:
            try:
                driver.get(link)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))  # Ensure page loads
                sign_in_popup_xpath = '//*[@id="public_post_contextual-sign-in"]/div/section'
                close_button_selector = '.modal__overlay--visible'
                try:
                    sign_in_popup = driver.find_element(By.XPATH, sign_in_popup_xpath)
                    if sign_in_popup.is_displayed():
                        #print("Sign-in popup detected, closing...")
                        close_button = driver.find_element(By.XPATH, close_button_selector)
                        close_button.click()
                        time.sleep(2)  # Allow some time for the popup to close
                except:
                    pass  # Continue if sign-in popup is not found
                elements = driver.find_elements(By.XPATH, "/html/body/main/section[1]/div/section[1]/article/div[3]/p")
                #print('Found element.')
                for e in elements:
                    copy = e.text
                    if len(copy) > 20:
                        # Check if the copy already exists in the Content table
                        cur.execute('SELECT id FROM Content WHERE copies = ?', (copy,))
                        existing_row = cur.fetchone()
                        if existing_row:
                            #print("Skipping duplicate copy")
                            continue
                        count+=1
                        print('original count:', count, '\n')
                        # Extract the published time
                        try:
                            # Wait for the post to load (ensure the target element is present)
                            time_xpath = '/html/body/main/section[1]/div/section[1]/article/div[1]/div/span/time'
                            time_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, time_xpath)))

                            # Get the text of the time element
                            date_text = time_element.text.strip()

                            # Convert the relative date to a regular datetime
                            post_date = convert_relative_date(date_text)

                        except Exception as e:
                            time_element = "Unknown"
                            print(f"Failed to extract published time: {e}")
                                
                        # Use current time if post_date is None
                        #post_date_str = post_date.strftime("%Y-%m-%d %H:%M:%S") if post_date else None
                        
                        cur.execute('''INSERT OR IGNORE INTO Content (copies, post_date) VALUES (?, ?)''', (copy, post_date.strftime("%Y-%m-%d %H:%M:%S")))
                        conn.commit()
                        
                        # Fetch the copies_id
                        cur.execute('SELECT id FROM Content WHERE copies = ?', (copy,))
                        copies_id = cur.fetchone()[0]
                        
                        # Update the Bing table with the copies_id
                        cur.execute('UPDATE Bing SET copies_id = ? WHERE url = ?', (copies_id, link))
                        conn.commit()
            except KeyboardInterrupt:
                    print('Terminating now...')
                    conn.commit()
                    break
            except Exception as e:
                    conn.commit()
                    print(f"Failed to open URL: {str(e)}")
    # Delete rows in Bing where url is null
    cur.execute('DELETE FROM Bing WHERE url IS NULL')
    cur.execute('DELETE FROM Bing WHERE copies_id IS NULL')
    conn.commit()

# Set the current time for file naming
x = datetime.datetime.now()
clock=x.strftime("%c")

# Scrape copies
posts_file = f'robert_webber_posts_{clock}.txt'
scrape_and_get_copies(driver, url_list)

# Retrieve data from the Content table
cur.execute('SELECT copies, post_date FROM Content')
posts = cur.fetchall()

# Open the output file in write mode
with open(posts_file, 'a', encoding='utf-8') as file:
    # Write headers or other information if needed
    file.write("Extracted Posts:\n\n")
    
    # Initialize count
    count = 0
    
    # Iterate through the retrieved rows
    for row in posts:
        count += 1
        post = row[0]
        post_date = row[1]
        
        # Write to file in the desired format
        file.write(f"Post {count}:\n")
        file.write(f"Post: {post_date}\n")
        file.write(f"Post Date: {post}\n\n")
        file.write("end\n\n\n")

# Print confirmation message
print(f"Successfully wrote {count} posts to {posts_file}")

# Close the WebDriver
driver.quit()
conn.commit()
cur.close
conn.close()
print('Driver closed.')
