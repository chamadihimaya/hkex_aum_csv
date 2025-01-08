#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import os
import logging


# In[2]:


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Starting AUM scraper")


# In[3]:


# CSV file path
csv_file_path = "aum_data.csv"


# In[4]:


# Set up Selenium options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode for automation
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")


# In[5]:


# Function to scrape AUM and update time for a given ETF
def get_aum_and_time(sym):
    try:
        url = f"https://www.hkex.com.hk/Market-Data/Securities-Prices/Exchange-Traded-Products/Exchange-Traded-Products-Quote?sym={sym}&sc_lang=en"
        driver.get(url)
        driver.implicitly_wait(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract AUM
        aum_element = soup.find('dt', {'class': 'ico_data col_aum'})
        aum_value = "N/A"
        if aum_element:
            aum_text = aum_element.text.strip()
            if aum_text.startswith("US$"):
                aum_text = aum_text[3:]
            if aum_text.endswith("M"):
                aum_value = float(aum_text[:-1]) * 1_000_000

        # Extract update time
        time_element = soup.find('dt', {'class': 'ico_data col_aum_date'})
        update_time = time_element.text.strip() if time_element else "N/A"

        return aum_value, update_time
    except Exception as e:
        logging.error(f"Error scraping data for {sym}: {e}")
        return "N/A", "N/A"


# In[6]:


# Function to get the previous value of AUM from the CSV
def get_previous_value(column_name):
    if os.path.exists(csv_file_path):
        try:
            df_existing = pd.read_csv(csv_file_path)
            if not df_existing.empty:
                # Get the last non-NA value for the column
                last_valid_value = df_existing[column_name].dropna().iloc[-1]
                return last_valid_value
        except Exception as e:
            logging.error(f"Error reading previous value from CSV: {e}")
    return "N/A"


# In[7]:


# Set up ChromeDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


# In[8]:


# Scrape data for ETFs
try:
    aum_9008, time_9008 = get_aum_and_time("9008")
    aum_9042, time_9042 = get_aum_and_time("9042")
    aum_9439, time_9439 = get_aum_and_time("9439")
finally:
    driver.quit()


# In[9]:


# Parse the date from the update time
try:
    date_str = time_9008.replace("as at ", "").strip() if time_9008 != "N/A" else datetime.now().strftime('%d %b %Y')
    current_date = datetime.strptime(date_str, '%d %b %Y').strftime('%Y-%m-%d')
except ValueError:
    current_date = datetime.now().strftime('%Y-%m-%d')


# In[10]:


# Check and replace "N/A" values with the previous day's value
if aum_9008 == "N/A":
    aum_9008 = get_previous_value("AUM_9008")
if aum_9042 == "N/A":
    aum_9042 = get_previous_value("AUM_9042")
if aum_9439 == "N/A":
    aum_9439 = get_previous_value("AUM_9439")


# In[11]:


# Save to CSV
def save_to_csv(data):
    try:
        if os.path.exists(csv_file_path):
            df_existing = pd.read_csv(csv_file_path)
        else:
            df_existing = pd.DataFrame(columns=["Date", "AUM_9008", "AUM_9042", "AUM_9439"])

        new_row = pd.DataFrame(data)
        df = pd.concat([df_existing, new_row], ignore_index=True).drop_duplicates(subset=["Date"])
        df.to_csv(csv_file_path, index=False)
        logging.info("Data saved to CSV successfully.")
    except Exception as e:
        logging.error(f"Error saving to CSV: {e}")

scraped_data = {
    "Date": [current_date],
    "AUM_9008": [aum_9008],
    "AUM_9042": [aum_9042],
    "AUM_9439": [aum_9439]
}


# In[12]:


save_to_csv(scraped_data)
logging.info("AUM scraper completed successfully.")


# In[ ]:




