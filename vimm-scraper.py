import os
import requests
from bs4 import BeautifulSoup
import re
import hashlib
from tqdm import tqdm
from functools import wraps
import time
# Constants
BASE_URL = "https://vimm.net"
DOWNLOAD_URL = "https://download3.vimm.net/download/"


def generate_vimm_url(system, section):
    base_url = "https://vimm.net/vault/"
    params = {
        "p": "list",
        "section": section,
        "system": system,
        "countries_select_all": "on",
        "action": "filters"
    }

    # Create the URL by joining the base URL and parameters
    url = base_url + "?" + "&".join([f"{key}={value}" for key, value in params.items()])

    return url

def retry(attempts=5, delay=3):
    """
    Retry wrapped function `attempts` times.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(
                        f"{func.__name__} attempt {i}/{attempts}",
                        str(e)
                    )
                    if i >= attempts:
                        print('attempted', attempts, 'skipping')
                    time.sleep(delay)

        return wrapper

    return decorator

s = requests.Session()

# change the user agent if you get 404/400 error
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
    if match:
        return match.group(1)
    return None

# Create a folder if it doesn't exist
def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# MD5 hash function
def calculate_md5(content):
    return hashlib.md5(content).hexdigest()

# Function to strip characters not allowed in Windows directory names
def strip_for_windows_directory_name(name):
    # Define a set of characters that are not allowed in Windows directory names
    invalid_chars = r'\/:*?"<>|'
    
    # Replace invalid characters with underscores
    stripped_name = ''.join(c if c not in invalid_chars else '_' for c in name)
    
    # Remove leading and trailing underscores
    stripped_name = stripped_name.strip('_')
    
    return stripped_name

def extract_media_id(soup):
    media_id_input = soup.find('input', {'name': 'mediaId'})
    if media_id_input:
        return media_id_input.get('value')
    return None


@retry()
def _download_rom(media_id, output_directory='.'):
    try:
        # Send an HTTP GET request to download the ROM
        response = s.get(DOWNLOAD_URL, params={'mediaId': media_id}, stream=True)
        print(response.url)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Get the filename from the Content-Disposition header if available
            content_disposition = response.headers.get('Content-Disposition')
            if content_disposition and 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[1].strip('" ')
            else:
                # If Content-Disposition header is not available or doesn't contain a filename, generate an MD5 hash-based filename
                filename = hashlib.md5(response.content).hexdigest()
            
            # Combine the filename with the output directory
            file_path = os.path.join(output_directory, filename)

            # Open the local file for writing in binary mode ('wb')
            with open(file_path, 'wb') as file, tqdm(
                total=int(response.headers.get('content-length', 0)),
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                desc=filename,
            ) as pbar:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
                        pbar.update(len(chunk))

            print(f"ROM '{filename}' has been downloaded successfully to '{output_directory}'.")
            return file_path
        else:
            print(f"Failed to download ROM with media id {media_id}. Status code: {response.status_code}")
            raise Exception("failed to download rom")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise Exception(str(e))


def download_rom(_url, output_directory='.'):
    rominfo_response = s.get(f"{BASE_URL}{_url}")
    print(rominfo_response.url)

    rominfo_soup = BeautifulSoup(rominfo_response.content.decode(), 'html.parser')
    media_id = extract_media_id(rominfo_soup)

    if media_id is not None:
        print('extracted media id', media_id)
        _download_rom(media_id, output_directory=output_directory)
    else:
        raise Exception('media_id not found!')
# Other functions (create_directory_if_not_exists, calculate_md5, strip_for_windows_directory_name, extract_id_from_url) remain the same

def main(system_letters):
    # system_letters is a dictionary where a system name is mapped to a uppercase letters from the abc, see bellow
    # todo: implement this shit
    # Iterate through systems and letters
     for system, letters in system_letters.items():
        for letter in letters:
                
            url = generate_vimm_url(system, letter)
            if letter.startswith("?"):
                url = f"{BASE_URL}/vault/{letter}"
            # Make an HTTP GET request
            response = s.get(url)
            
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Parse the HTML content
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all links and filter for valid URLs
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    href = link['href']
                    game_name = link.get_text()
                    game_id = extract_id_from_url(href)
                    if game_id is not None:
                        game_cover_url = f"{BASE_URL}/image.php?type=screen&id={game_id}"
                        print(f"Checking {game_name}...")
                        dir_name = f'./vimm/{system}/{game_name}/'
                        create_directory_if_not_exists(dir_name)
                        download_rom(href,dir_name)

if __name__ == "__main__":
    # List of systems and uppercase letters A-Z
    systems = [
        "NES", "SMS", "Genesis", "SNES", "32X", "Saturn", "PS1", "N64",
        "Dreamcast", "PS2", "GameCube", "Xbox", "Xbox360", "PS3", "Wii", "WiiWare",
        "GB", "GBC", "GBA", "GG", "DS", "VB", "PSP"
    ]

    # Initialize an empty dictionary to store selected systems and their letter ranges
    system_letters = {}

    # Prompt the user to select systems and letter ranges
    for system in systems:
        letters_input = input(f"Select letters for {system} (e.g., ABC, include # for games starting with numbers, or press Enter for all, or a / for none): ")
        if letters_input:
            if '/' == letters_input.strip():
                # Skip this system if '/' is selected
                continue
            letter_range = [letter.upper() for letter in letters_input]
            system_letters[system] = letter_range

            if '#' in system_letters[system]:
                # Define the item you want to replace
                item_to_replace = '#'
                new_value = '?p=list&system={}&section=number'.format(system)  # Replace '#' with 'X'
                # Use a list comprehension to replace all occurrences of the item
                system_letters[system] = [new_value if item == item_to_replace else item for item in system_letters[system]]
        else:
            system_letters[system] = ['?p=list&system={}&section=number'.format(system)] + [*'ABCDEFGHIJKLMNOPQRSTUVXYZ']

    if not system_letters:
        print("No systems selected. Exiting.")
    else:
        main(system_letters)

