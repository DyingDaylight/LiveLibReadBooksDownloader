# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from requests.exceptions import ConnectTimeout, ReadTimeout
import requests
import argparse
import json
import time
import csv
import sys
import re


def parse_last_page(source):
    last_page_match = re.search(r'class="pagination-page pagination-wide" title="Последняя страница".*~(\d+)', source) 
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
            source.encoding = 'utf-8'    
            print(source.status_code)
            
            return source
        except (ConnectTimeout, ReadTimeout):
            attempts += 1
            time.sleep(5) 
            print(f'Retry {attempts}')
  
  
def write_source(source, i): 
    with open(f'read_page_{page}.txt', 'wb') as f:
        f.write(source.content)
        print(f'Written to file\n')


def read_source(page=1):
    with open(f'read_page_{page}.txt', 'r', encoding="utf-8") as f:
        source = f.read()
        return source
        
        
def parse_page(source):
    classes = {'name': ('a', 'brow-book-name with-cycle'), 
               'author': ('a', 'brow-book-author'), 
               'series': ('a', 'cycle-title'), 
               'rating': ('span', 'rating-value'),
               }
    book_dicts = []
    
    soup = BeautifulSoup(source, "html.parser")
    book_cards = soup.find_all("div", class_="book-item-manage")
    
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
    print(f"Writing {len(dicts)}")
    
    fields = ['name', 'author', 'series', 'rating', 'link']
    with open('bookdb.csv', 'w', newline='', encoding="utf-8") as file: 
        writer = csv.DictWriter(file, fieldnames = fields)
        writer.writeheader() 
        writer.writerows(dicts)


def download(base_url, start=1):
    source = get_source(base_url).text
    last_page = parse_last_page(source)
    yield source
    
    for i in range(start + 1, 3):
        if i % 10:
            yield source
            time.sleep(3)
            
        source = get_source(base_url, i)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="User name to parse read books for", type=str)
    args = parser.parse_args()
    
    username = args.username    
    base_url = f'https://www.livelib.ru/reader/{username}/read'
    print(f"Parsing books for {username}")
    print(f"from {base_url}")

    book_dicts = []
   
    for i, source in enumerate(download(base_url), 1):
        print(f'Parsing page {i}')
        
        books = parse_page(source)
        book_dicts.extend(books)
        
    write_to_csv(book_dicts)
