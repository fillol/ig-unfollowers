import json
import urllib.request
import re
import time
import logging
import os
import sys
import argparse

THRESHOLD = 10000
CACHE_FILE_PATH = 'follower_count_cache.json'
RESULT_FILE_PATH = 'filtered_list.txt'
follower_count_cache = {}


def load_follower_count_cache_from_file(cache_file_path):
    """Loads the follower count cache from a JSON file."""
    try:
        if os.path.exists(cache_file_path):
            with open(cache_file_path, 'r', encoding='utf-8') as file:
                loaded_cache = json.load(file)
                logging.info(f"Cache loaded from file: {cache_file_path} (items: {len(loaded_cache)})")
                return loaded_cache
    except FileNotFoundError:
        logging.info("Cache file not found. Initialized empty cache.")
    except json.JSONDecodeError as json_error:
        logging.error(f"JSON decode error in cache file {cache_file_path}: {json_error}. Initialized empty cache.")
    except Exception as e:
        logging.error(f"Error loading cache from file {cache_file_path}: {e}. Initialized empty cache.")
    return {}


def save_follower_count_cache_to_file(cache_file_path, cache_data):
    """Saves the follower count cache data to a JSON file."""
    try:
        with open(cache_file_path, 'w', encoding='utf-8') as file:
            json.dump(cache_data, file, ensure_ascii=False, indent=4)
        logging.info(f"Cache saved to file: {cache_file_path} (items: {len(cache_data)})")
    except Exception as e:
        logging.error(f"Error saving cache to file {cache_file_path}: {e}")


def save_result_list_to_file(result_file_path, result_list):
    """Saves the list of usernames to a text file."""
    try:
        with open(result_file_path, 'w', encoding='utf-8') as file:
            for username in result_list:
                file.write(username + '\n')
        logging.info(f"Filtered list saved to file: {result_file_path} (users: {len(result_list)})")
    except Exception as e:
        logging.error(f"Error saving filtered list to file {result_file_path}: {e}")


def safe_load_json_followers(file_path):
    """Safely loads the list of followers from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        logging.error(f"JSON file not found: {file_path}")
        return []
    except json.JSONDecodeError as json_error:
        logging.error(f"JSON decode error in file {file_path}: {json_error}")
        return []
    except Exception as e:
        logging.error(f"Unexpected error loading file {file_path}: {e}")
        return []

    result = []
    for element in data:
        try:
            username = element['string_list_data'][0]['value']
            result.append(username)
        except (KeyError, IndexError):
            logging.warning(f"Malformed follower JSON element, ignored: {element}")
            continue
    return result


def safe_load_json_following(file_path, key):
    """Safely loads the list of followings from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        logging.error(f"JSON file not found: {file_path}")
        return []
    except json.JSONDecodeError as json_error:
        logging.error(f"JSON decode error in file {file_path}: {json_error}")
        return []
    except Exception as e:
        logging.error(f"Unexpected error loading file {file_path}: {e}")
        return []

    result = []
    for element in data.get(key, []):
        try:
            username = element['string_list_data'][0]['value']
            result.append(username)
        except (KeyError, IndexError):
            logging.warning(f"Malformed following JSON element, ignored: {element}")
            continue
    return result


def fetch_follower_count(username, max_retries=3, backoff_factor=2):
    """Retrieves the follower count of an Instagram user."""
    cache_hit_flag = False
    if username in follower_count_cache:
        logging.info(f"Cache hit for {username}, follower count: {follower_count_cache[username]}")
        return follower_count_cache[username], True

    url = f"https://www.instagram.com/{username}/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    request = urllib.request.Request(url, headers=headers)
    delay = 1
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.getcode() != 200:
                    logging.warning(f"HTTP Response {response.getcode()} for {username}")
                    raise Exception(f"HTTP status {response.getcode()}")
                page_content = response.read().decode('utf-8')

                meta_tag_match = re.search(r'<meta\s+property=["\']og:description["\']\s+content=["\']([^"\']*)["\']', page_content, re.IGNORECASE)
                if meta_tag_match:
                    meta_content = meta_tag_match.group(1)
                    follower_match = re.search(r"([0-9.,]+)([MK]?)\s*follower(?:s)?(?:,|)?", meta_content, re.IGNORECASE)
                    if follower_match:
                        count_str = follower_match.group(1).replace(",", ".")
                        unit_indicator = follower_match.group(2).upper()
                        count = float(count_str)
                        if unit_indicator == 'M':
                            count *= 1000000
                        elif unit_indicator == 'K':
                            count *= 1000
                        follower_count = int(count)
                        follower_count_cache[username] = follower_count
                        return follower_count, False
                else:
                    logging.warning(f"Attempt {attempt}: Meta tag 'og:description' not found for {username}.")
                    return None, False

        except (urllib.error.HTTPError, urllib.error.URLError) as url_error:
            logging.error(f"Attempt {attempt}: HTTP/URL error for {username}: {url_error}")
        except Exception as e:
            logging.error(f"Attempt {attempt}: Generic error for {username}: {e}")

        time.sleep(delay)
        delay *= backoff_factor

    return None, False


def update_progress_bar(percentage, operation_text_length):
    """Updates the progress bar at the end of the line (right-aligned) in the terminal."""
    terminal_width = os.get_terminal_size().columns
    bar_length = 20
    percentage_string_length = 6
    required_spaces = terminal_width - operation_text_length - bar_length - percentage_string_length - 2
    spaces_string = " " * max(0, required_spaces)

    filled_length = int(bar_length * percentage / 100)
    bar_graphic = '=' * filled_length + '-' * (bar_length - filled_length)

    if percentage == 100:
        percentage_output = f'{int(percentage)}%'
    else:
        percentage_output = f'{percentage:.1f}%'

    sys.stdout.write(f'{spaces_string}[{bar_graphic}] {percentage_output}')
    sys.stdout.flush()


def main():
    """Main function of the script."""
    followers_file = 'followers.json'
    following_file = 'following.json'
    cache_file = CACHE_FILE_PATH
    result_file = RESULT_FILE_PATH

    parser = argparse.ArgumentParser(description="Script to filter non-reciprocal Instagram users.")
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable detailed logging (INFO level).')
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
    else:
        logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(levelname)s: %(message)s')

    global follower_count_cache
    follower_count_cache = load_follower_count_cache_from_file(cache_file)

    followers_usernames = safe_load_json_followers(followers_file)
    following_usernames = safe_load_json_following(following_file, 'relationships_following')
    non_reciprocal_usernames = set(following_usernames) - set(followers_usernames)
    print("")
    print(f"Loaded {len(followers_usernames)} followers and {len(following_usernames)} followings. Found {len(non_reciprocal_usernames)} non-reciprocal accounts.")
    print("")

    result_list = []
    total_users = len(non_reciprocal_usernames)
    processed_users_count = 0

    for username in non_reciprocal_usernames:
        processed_users_count += 1
        percentage_complete = (processed_users_count / total_users) * 100

        operation_text = f"Processing: {username}"
        operation_text_length = len(operation_text)

        print(operation_text, end="")
        update_progress_bar(percentage_complete, operation_text_length)
        print("")

        follower_count, cache_hit = fetch_follower_count(username)
        if not cache_hit:
            time.sleep(1)

        if follower_count is None:
            logging.info(f"{username} included due to missing follower count data.")
            result_list.append(username)
        elif follower_count <= THRESHOLD:
            result_list.append(username)
        else:
            logging.info(f"{username} excluded: {follower_count} followers (threshold exceeded).")

    update_progress_bar(100, operation_text_length=0)
    print("")
    print("")
    print("\nProcessing completed.")

    logging.info("Final list (filtered):")
    print("\nResult List:")
    for user in sorted(result_list):
        print(user)

    save_follower_count_cache_to_file(cache_file, follower_count_cache)
    save_result_list_to_file(result_file, result_list)


if __name__ == '__main__':
    main()
