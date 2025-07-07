import pandas as pd
from selenium import webdriver
from datetime import datetime
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
#from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re

def scrape_ipo_subscription_data_from_url(url):
    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/chromium"  ## for docker
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--incognito")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-setuid-sandbox")

    try:
        #service = Service(ChromeDriverManager().install())
        #driver = webdriver.Chrome(service=service, options=chrome_options)
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(60)
    except Exception as e:
        print(f"Error initializing WebDriver: {e}")
        return None

    company_name = "N/A"
    qib_sub = "N/A"
    nii_sub = "N/A"
    rii_sub = "N/A"
    total_sub = "N/A"
    basis_allotment = "N/A"
    listing_date = "N/A"
    ipo_issue_size = "N/A"
    gmp_on_allotment = "N/A"
    ipo_price_on_allotment = "N/A"

    def normalize_date(date_str):
        # Remove ordinal suffixes like 'th', 'st', 'nd', 'rd'
        cleaned = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
        # Try parsing with known formats
        for fmt in ("%d %b %Y", "%d-%m-%Y", "%d %B %Y", "%d-%b-%Y"):
            try:
                return datetime.strptime(cleaned.strip(), fmt)#.strftime("%Y-%m-%d")
            except Exception:
                continue
        return None

    try:
        print(f"Navigating to: {url}")
        driver.get(url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//caption[contains(text(), 'IPO Bidding Live Updates from BSE, NSE')]"))
        )

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        title_match = re.search(r'^(.*?) IPO', driver.title)
        if title_match:
            company_name = title_match.group(1).strip()
        else:
            url_parts = url.split('/')
            for part in url_parts:
                if '-ipo' in part:
                    company_name = part.replace('-ipo', '').replace('-', ' ').title()
                    break

        # --- IPO Issue Size logic ---
        details_table = soup.find('table', class_='table table-bordered table-striped table-hover w-auto')
        if details_table:
            for row in details_table.find_all('tr'):
                tds = row.find_all('td')
                if len(tds) >= 2:
                    label = tds[0].get_text(strip=True)
                    if 'Issue Size' in label:
                        ipo_issue_size = tds[1].get_text(strip=True)
                        break
                for td in tds:
                    if td.has_attr('data-title') and 'Issue Size' in td['data-title']:
                        ipo_issue_size = td.get_text(strip=True)
                        break

        # Extract IPO Dates
        date_tables = soup.find_all('table', class_='table table-bordered table-striped table-hover w-auto')
        for table in date_tables:
            for row in table.find_all('tr'):
                cols = row.find_all('td')
                if len(cols) < 2:
                    continue
                label = cols[0].text.strip()
                value = cols[1].text.strip()
                if 'Allotment' in label:
                    basis_allotment = value
                    basis_allotment=normalize_date(basis_allotment)
                elif 'Listing Date' in label:
                    listing_date = value
                    listing_date=normalize_date(listing_date)

        # Extract subscription data (Day 3)
        ipo_table = soup.find('caption', string=lambda text: text and 'IPO Bidding Live Updates from BSE, NSE' in text)
        if ipo_table:
            table_element = ipo_table.find_parent('table')
            if table_element:
                rows = table_element.find('tbody').find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if any('Day=3' in c.get('data-title', '') or c.get('data-title', '').endswith('-Day3') for c in cells):
                        qib_td = row.find('td', {'data-title': lambda x: x and 'QIB-Day3' in x})
                        nii_td = row.find('td', {'data-title': lambda x: x and 'NII-Day3' in x})
                        rii_td = row.find('td', {'data-title': lambda x: x and 'RII-Day3' in x})
                        total_td = row.find('td', {'data-title': lambda x: x and 'Total-Day3' in x})

                        qib_sub = qib_td.get_text(strip=True) if qib_td else "N/A"
                        nii_sub = nii_td.get_text(strip=True) if nii_td else "N/A"
                        rii_sub = rii_td.get_text(strip=True) if rii_td else "N/A"
                        total_sub = total_td.get_text(strip=True) if total_td else "N/A"
                        break

        # --- GMP and IPO Price on Basis of Allotment Date ---
        if basis_allotment != "N/A":
            gmp_url = url.replace("/ipo", "/gmp")
            print(f"Navigating to GMP page: {gmp_url}")
            driver.get(gmp_url)
            time.sleep(3)
            gmp_soup = BeautifulSoup(driver.page_source, 'html.parser')
            gmp_table = gmp_soup.find('table', class_='table table-bordered table-striped w-auto')

            if gmp_table:
                for row in gmp_table.find('tbody').find_all('tr'):
                    date_td = row.find('td', {'data-title': 'GMP Date'})
                    ipo_price_td = row.find('td', {'data-title': 'GMP Price'})
                    gmp_td = row.find('td', {'data-title': 'GMP'})
                    
                    if date_td and ipo_price_td and gmp_td:
                        gmp_date = date_td.get_text(separator=' ',strip=True).split()[0]
                        gmp_date=normalize_date(gmp_date)

                        if gmp_date == basis_allotment:
                            ipo_price_on_allotment = ipo_price_td.get_text(strip=True)
                            gmp_on_allotment = gmp_td.get_text(strip=True).replace('\xa0', ' ')
                            break




    except Exception as e:
        print(f"Error scraping data from {url}: {e}")
    finally:
        driver.quit()

    input_ipo_details_dict= {
        "Company Name": company_name,
        "IPO Link": url,
        "Basis of Allotment Date": basis_allotment,
        "IPO Listing Date": listing_date,
        "IPO Issue Size": ipo_issue_size,
        "QIB Subscription": qib_sub,
        "NII Subscription": nii_sub,
        "RII Subscription": rii_sub,
        "Total Subscription": total_sub,
        "GMP on Allotment Date": gmp_on_allotment,
        "IPO Price on Allotment Date": ipo_price_on_allotment
    }

    return input_ipo_details_dict

# Example usage
#if __name__ == "__main__":
#    test_url = "https://www.investorgain.com/ipo/crizac-ipo/1308/"
#    result = scrape_ipo_subscription_data_from_url(test_url)
#    print(result)
