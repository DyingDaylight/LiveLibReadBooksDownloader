# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from requests.exceptions import ConnectTimeout, ReadTimeout
import requests
import argparse
import time
import csv
import sys
import re


def parse_last_page(source):
    last_page_match = re.search(r'class="pagination-page pagination-wide" title="Последняя страница".*~(\d+)', source) 
    if not last_page_match:
        raise ValueError("Number of pages is not found")
        
    last_page = int(last_page_match.group(1))
    print(f'Parsing {last_page} pages')
    
    return last_page


def get_source(base_url, page=1, max_attempts=15):
    url = base_url if page == 1 else f'{base_url}/~{page}'
    print(f'\nDownloading from {url}')

    attempts = 0
    while attempts < max_attempts:
        try:
            source = requests.get(url, timeout=(3.05, 27))
            if not source:
                raise ValueError("Cannot load the page")
               
            print("" if attempts == 0 else "\n", end = "")
            print(f"Status code: {source.status_code}")
            if source.status_code != 200:
                raise ValueError("Cannot load the page")
            
            source.encoding = 'utf-8' 
            text =  source.text

            if "captcha-show" in text:
                print("Too many requests to the site. Parsing continue in a couple of minutes...")
                time.sleep(120)
                raise ReadTimeout
            
            return text
        except (ConnectTimeout, ReadTimeout):
            attempts += 1
            time.sleep(10) 
            print(f"\rRetry attempt {attempts}", end = "")
            
    raise ValueError("Cannot load the page")
        
        
def parse_page(source):
    classes = {'name': ('a', 'brow-book-name with-cycle'), 
               'author': ('a', 'brow-book-author'), 
               'series': ('a', 'cycle-title'), 
               'rating': ('span', 'rating-value'),
               }
    book_dicts = []
    
    soup = BeautifulSoup(source, "html.parser")
    book_cards = soup.find_all("div", class_="book-item-manage")
    
    if not book_cards:
        print(source)
        raise ValueError("No books found on the page")
    
    for book_card in book_cards:
        book_dict = {}
        
        for field, data in classes.items():
            element = book_card.find(data[0], class_=data[1])
            if element:
                book_dict[field] = element.text

        element = book_card.find("a", class_="brow-book-name with-cycle")
        book_dict['link'] = element['href']
        book_dicts.append(book_dict)
        
    return book_dicts


def write_to_csv(dicts):
    print(f"\nWriting {len(dicts)}")
    
    fields = ['author', 'name', 'series', 'rating', 'link']
    with open('bookdb.csv', 'w', newline='', encoding="utf-8") as file: 
        writer = csv.DictWriter(file, fieldnames = fields)
        writer.writeheader() 
        writer.writerows(dicts)


def download(base_url, start=1):
    source = get_source(base_url)    
    last_page = parse_last_page(source)
    yield source
    
    for i in range(start + 1, last_page):
        source = get_source(base_url, i)
        yield source
           

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="User name to parse read books for", type=str)
    args = parser.parse_args()
    
    username = args.username    
    base_url = f'https://www.livelib.ru/reader/{username}/read'
    print(f"Parsing books for {username}")
    print(f"From: {base_url}")

    book_dicts = []
   
    try:
        for i, source in enumerate(download(base_url)):
            print(f'Parsing page {i + 1}')
            
            books = parse_page(source)
            book_dicts.extend(books)
            
            if i % 10 == 0:
                time.sleep(60)
            else:
                time.sleep(10)
            
        write_to_csv(book_dicts)
    except ValueError as er:
        print(f"Something went wrong: {er}")
        sys.exit(0)
