from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import argparse
import time
import csv


def read_books_from_site(url, driverpath):
    print(f"\nParsing books...")
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(driverpath)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(chrome_options)

    driver.get(base_url)
    assert f"{username} прочитал" in driver.title

    book_dicts = []

    while True:
        try:
            #popup = driver.find_element(By.CLASS_NAME, "popup-accept-kv modal")
            popup = driver.find_element(By.XPATH, '//div[starts-with(@class, "popup")]')
            close_button = popup.find_element(By.CLASS_NAME, "btn-close")
            driver.execute_script("arguments[0].click();", close_button)
            print("popup closed")
        except NoSuchElementException:
            pass
            
        book_cards = driver.find_elements(By.CLASS_NAME, "book-item-manage")
        
        for book_card in book_cards:
            book_dict = {}
        
            book_dict['name'] = book_card.find_element(By.CSS_SELECTOR, "a.brow-book-name").text

            try:
                book_dict['author'] = book_card.find_element(By.CLASS_NAME, "brow-book-author").text
            except NoSuchElementException:
                book_dict['author'] = ""
            
            book_dict['rating'] = book_card.find_element(By.CSS_SELECTOR, "span.rating-value").text
            
            try:
                book_dict['series'] = book_card.find_element(By.CSS_SELECTOR, "a.cycle-title").text
            except NoSuchElementException:
                book_dict['series'] = ""
            
            print(book_dict)
            book_dicts.append(book_dict)
            
        next_image = driver.find_element(By.CSS_SELECTOR, "span.i-pager-next")
        next_button = next_image.find_element(By.XPATH, '..')
        
        href = next_button.get_attribute("href")
        if not href:
            break
            
        driver.execute_script("arguments[0].click();", next_button)
        
    driver.close()
    
    return book_dicts
    

def write_to_csv(dicts):
    print(f"\nWriting {len(dicts)}")
    
    fields = ['author', 'name', 'series', 'rating', 'link']
    with open('bookdb.csv', 'w', newline='', encoding="utf-8") as file: 
        writer = csv.DictWriter(file, fieldnames = fields)
        writer.writeheader() 
        writer.writerows(dicts)
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="User name to parse read books for", type=str)
    parser.add_argument("driverpath", help="User name to parse read books for", type=str, nargs='?',
                        default=r"D:/Workspaces/SeleniumWebDrivers/chromedriver-win64/chromedriver.exe")
    args = parser.parse_args()
    
    username = args.username 
    driverpath = args.driverpath   
    
    base_url = f'https://www.livelib.ru/reader/{username}/read'
    #base_url = f'https://www.livelib.ru/reader/{username}/read/listview/smalllist/~134'
    print(f"Parsing books for {username}")
    print(f"From: {base_url}")
    
    book_dicts = read_books_from_site(base_url, driverpath)

    write_to_csv(book_dicts)
        