from bs4 import BeautifulSoup
from requests.exceptions import ConnectTimeout, ReadTimeout
import requests
import argparse
import time  
import json
import csv
import sys


def log_in(username, password, max_attempts=15):
    print(f'\nEstablishing session...')
    
    attempts = 0
    while attempts < max_attempts:   
        try:
            response = requests.get("https://www.livelib.ru/")
        except (ConnectTimeout, ReadTimeout):
            attempts += 1
            time.sleep(10) 
            print(f"\rRetry attempt {attempts}", end = "")
    
    print("" if attempts == 0 else "\n", end = "")
    
    if attempts == max_attempts:
        raise ValueError("Cannot establish connection")
        
    print("Status code: ", response.status_code)
    
    session = requests.session()
    
    print(f'\nLogging in...')
    
    payload = {'user[login]': username,
               'user[password]': password,
               #'current_url': 'https://www.livelib.ru/',
               #'is_new_design': '112019',
               #'rebuild_menu': 'false',
               #'popup': 'regform',
               #'user[redirect]': '',
               #'user[onclick]': '',
               #'source': ''
               }
               
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
               "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
               #"accept": "*/*",
               #"Accept-Encoding": "gzip, deflate, br",
               "X-Requested-With": "XMLHttpRequest"}
        
    login_url = "https://www.livelib.ru/account/login"
    
    attempts = 0
    while attempts < max_attempts:   
        try:
            response = session.post(login_url, data=payload, headers=headers)
        except (ConnectTimeout, ReadTimeout):
            attempts += 1
            time.sleep(10) 
            print(f"\rRetry attempt {attempts}", end = "")
    
    print("" if attempts == 0 else "\n", end = "")
        
    if attempts == max_attempts:
        raise ValueError("Cannot log in")
        
    print("Status code: ", response.status_code)
            
    response.encoding = 'utf-8'
            
    try:
        response_json = json.loads(response.text)
        if response_json.get("error_code") != 0:
            raise ValueError(response_json.get("message"))
            
        print("Logged in!") 
    except json.JSONDecodeError as e:
        raise ValueError("Login failed!")
        
    print(response_json)
    print(response.headers)
    print(response.request.headers)
        
    return session
    
def get_source(session, base_url, max_attempts=15):
    attempts = 0
    while attempts < max_attempts:
        try:
            print(f'\nDownloading from {base_url}')
            
            headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            
            source = session.get(base_url, timeout=(80, 80), headers=headers)
            
            print("" if attempts == 0 else "\n", end = "")
            
            if not source:
                raise ValueError("Cannot load the page")
                
            print(f"Status code: {source.status_code}")
            
            if source.status_code != 200:
                raise ValueError("Cannot load the page")
                
            source.encoding = 'utf-8'
            return source.text
        except (ConnectTimeout, ReadTimeout):
            attempts += 1
            time.sleep(10) 
            print(f"\rRetry attempt {attempts}", end = "")
            
    raise ValueError("Cannot load the page")

        
def parse_page(source):
    print(f"\nParsing page...")

    classes = {'name': ('a', 'brow-book-name with-cycle'), 
               'author': ('a', 'brow-book-author'), 
               'series': ('a', 'cycle-title'), 
               'rating': ('span', 'rating-value'),
               }
    book_dicts = []
    
    soup = BeautifulSoup(source, "html.parser")
    rows = soup.find_all("tr")
    
    date = ""
    for row in rows:
        element = row.find("h2")
        if element:
            date = element.text
            continue
            
        book_dict = {}
        
        elements = row.find_all("a")
        book_dict['name'] = elements[0].text
        
        if len(elements) > 1:
            book_dict['author'] = elements[1].text       

        element = row.find("span", class_="rating")
        book_dict['rating'] = element.get("title")  

        book_dict['date'] = date       

        book_dicts.append(book_dict)
        
    return book_dicts


def write_to_csv(dicts):
    filename = 'bookdb.csv'
    
    print(f"\nWriting {len(dicts)} books to {filename}...")
    
    fields = ['name', 'author', 'rating', 'date']
    with open(filename, 'w', newline='', encoding="utf-8") as file: 
        writer = csv.DictWriter(file, fieldnames = fields)
        writer.writeheader() 
        writer.writerows(dicts)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    subs.required = True
    
    online_parser = subs.add_parser('online', help='Download book list')
    online_parser.add_argument("username", help="User name to parse read books for", type=str)
    online_parser.add_argument("password", help="Password from LiveLib account", type=str)
    online_parser.set_defaults(type="online")
    
    from_file_parser = subs.add_parser('from_file', help='Read books from html file')
    from_file_parser.add_argument("filename", help="Path to html file")
    from_file_parser.set_defaults(type="file")
    
    args = parser.parse_args()
    
    if args.type == "online":
        username = args.username    
        password = args.password
        base_url = f'https://www.livelib.ru/reader/{username}/read/print'
        
        print(f"Parsing books for {username}")
        print(f"From: {base_url}")
    
        try:
            session = log_in(username, password)
            source = get_source(session, base_url)
            
            #with open("source.html", "w", encoding="utf-8") as f:
            #    f.write(source)
        except ValueError as er:
            print(f"Something went wrong: {er}")
            sys.exit(0)
            
    elif args.type == "file":
        path = args.filename
    
        print(f"Parsing books from file {path}")
    
        try:
            with open(path, "r", encoding="utf-8") as f:
                source = f.read()
        except FileNotFoundError as er:
            print(f"Unable to read file {path}")
            sys.exit(0)
        
    book_dicts = parse_page(source)

    write_to_csv(book_dicts)
