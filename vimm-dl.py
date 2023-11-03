# Standalone Vimm.net downloader
# Downloads a single rom from a url
# https://https://github.com/amir16yp/vimm-scraper/


import os
import requests
from bs4 import BeautifulSoup
import re
import hashlib
from tqdm import tqdm
from functools import wraps
import time
from sys import argv

# Constants
DOWNLOAD_URLS = [
    "https://download3.vimm.net/download/",
    "https://download2.vimm.net/download/",
    "https://download.vimm.net/download/"
]

# Decorator to retry a function
def retry(attempts=2, delay=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal attempts
            for i in range(attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Attempt {i+1}/{attempts} failed: {e}")
                    time.sleep(delay)
                    attempts -= 1
                    if attempts == 0:
                        print("All retry attempts failed.")
        return wrapper
    return decorator

# Initialize session
s = requests.Session()
s.headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
    'Connection': 'keep-alive', 
    'Referer': 'https://vimm.net/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.43',
}

# Function to check if a URL matches the pattern and extract the ID
def extract_id_from_url(url):
    match = re.match(r"/vault/(\d+)/?$", url)
    return match.group(1) if match else None

# MD5 hash function
def calculate_md5(content):
    return hashlib.md5(content).hexdigest()

# Function to extract media ID
def extract_media_id(soup):
    media_id_input = soup.find('input', {'name': 'mediaId'})
    return media_id_input.get('value') if media_id_input else None

@retry()
def _download_rom(media_id):
    for download_url in DOWNLOAD_URLS:
        try:
            response = s.get(download_url, params={'mediaId': media_id}, stream=True)
            if response.status_code == 200:
                content_disposition = response.headers.get('Content-Disposition')
                filename = re.findall("filename=(.+)", content_disposition)[0].strip('" ') if content_disposition else calculate_md5(response.content)
                with open(filename, 'wb') as file, tqdm(
                    total=int(response.headers.get('content-length', 0)),
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=filename
                ) as pbar:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
                            pbar.update(len(chunk))
                print(f"ROM '{filename}' downloaded successfully.")
                return
            else:
                print(f"Download failed with status code: {response.status_code}")
        except Exception as e:
            print(f"Error occurred: {e}")
    raise Exception("Download failed for all URLs.")

def download_rom(_url):
    rominfo_response = s.get(_url)
    rominfo_soup = BeautifulSoup(rominfo_response.content.decode(), 'html.parser')
    media_id = extract_media_id(rominfo_soup)

    if media_id:
        print(f'Extracted media ID: {media_id}')
        _download_rom(media_id)
    else:
        raise Exception('Media ID not found!')

if __name__ == "__main__":
    if len(argv) > 1:
        download_rom(argv[1])
    else:
        print("Usage: vimm-dl.py <URL>")
