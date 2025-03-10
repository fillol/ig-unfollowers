import json
import time
import logging
import os
import sys
import argparse


try:
    from instagrapi import Client
    instagrapi_available = True
except ImportError:
    print("\nWarning: 'instagrapi' library not found. The script will fall back to JSON mode.")
    print("To use the API mode, install 'instagrapi' with: pip install instagrapi\n")
    instagrapi_available = False
    Client = None


THRESHOLD = 10000
CACHE_FILE_PATH = 'follower_count_cache.json'
RESULT_FILE_PATH = 'filtered_list.txt'
FOLLOWER_FILE_DEFAULT = 'followers.json'
FOLLOWING_FILE_DEFAULT = 'following.json'
follower_count_cache = {}
USERNAME_INSTAGRAM = None
PASSWORD_INSTAGRAM = None


def load_follower_count_cache_from_file(cache_file_path):
    """Load follower count cache from JSON file."""
    try:
        if os.path.exists(cache_file_path):
            with open(cache_file_path, 'r', encoding='utf-8') as file:
                loaded_cache = json.load(file)
                logging.info(f"Cache loaded from file: {cache_file_path} (elements: {len(loaded_cache)})")
                return loaded_cache
    except FileNotFoundError:
        logging.info("Cache file not found. Initializing empty cache.")
    except json.JSONDecodeError as json_error:
        logging.error(f"JSON decode error in cache file {cache_file_path}: {json_error}. Initializing empty cache.")
    except Exception as e:
        logging.error(f"Error loading cache from file {cache_file_path}: {e}. Initializing empty cache.")
    return {}


def save_follower_count_cache_to_file(cache_file_path, cache_data):
    """Save follower count cache data to JSON file."""
    try:
        with open(cache_file_path, 'w', encoding='utf-8') as file:
            json.dump(cache_data, file, ensure_ascii=False, indent=4)
        logging.info(f"Cache saved to file: {cache_file_path} (elements: {len(cache_data)})")
    except Exception as e:
        logging.error(f"Error saving cache to file {cache_file_path}: {e}")


def save_result_list_to_file(result_file_path, result_list):
    """Save the list of usernames to a text file."""
    try:
        with open(result_file_path, 'w', encoding='utf-8') as file:
            for username in result_list:
                file.write(username + '\n')
        logging.info(f"Filtered list saved to file: {result_file_path} (users: {len(result_list)})")
    except Exception as e:
        logging.error(f"Error saving filtered list to file {result_file_path}: {e}")


def safe_load_json_followers(file_path):
    """Safely load followers list from JSON file."""
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
    """Safely load following list from JSON file."""
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


def fetch_follower_count_from_api(username, cl=None):
    """Fetch follower count using Instagrapi API."""
    cache_hit_flag = False
    if username in follower_count_cache:
        logging.info(f"Cache hit for {username}, follower count: {follower_count_cache[username]}")
        return follower_count_cache[username], True

    try:
        if cl is None:
            temp_cl = Client()
            if USERNAME_INSTAGRAM and PASSWORD_INSTAGRAM:
                try:
                    temp_cl.login(USERNAME_INSTAGRAM, PASSWORD_INSTAGRAM)
                    logging.info("API login successful for follower count fetch in JSON mode.")
                except Exception as login_error:
                    logging.warning(f"API login failed for follower count fetch in JSON mode (continuing without login): {login_error}")
            cl = temp_cl

        user_info = cl.user_info_by_username_v2(username)
        follower_count = user_info.follower_count
        follower_count_cache[username] = follower_count
        return follower_count, False
    except Exception as e:
        logging.error(f"Instagrapi API error for {username}: {e}")
        return None, False


def update_progress_bar(percentage, operation_text_length):
    """Update progress bar at the end of the line."""
    terminal_width = os.get_terminal_size().columns
    bar_length = 20
    percentage_string_length = 6
    needed_spaces = terminal_width - operation_text_length - bar_length - percentage_string_length - 2
    spaces_string = " " * max(0, needed_spaces)

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
    cache_file = CACHE_FILE_PATH
    result_file = RESULT_FILE_PATH
    followers_file = FOLLOWER_FILE_DEFAULT
    following_file = FOLLOWING_FILE_DEFAULT

    parser = argparse.ArgumentParser(description="Script to filter non-reciprocal Instagram users.\n \
                                     By default, it uses Instagram API if 'instagrapi' library is installed.\n \
                                     Otherwise, or if --json option is used, it uses exported JSON files.",
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--json', action='store_true', help=f"Force use of JSON files for followers/following\n \
                                     (files '{followers_file}' and '{following_file}' in current directory).\n \
                                     API credentials are not needed in this mode.")
    parser.add_argument('-u', '--username', type=str, help='Instagram username for API authentication (optional for public profiles).')
    parser.add_argument('-p', '--password', type=str, help='Instagram password for API authentication (optional for public profiles).')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable detailed logging (INFO level).')

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
    else:
        logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(levelname)s: %(message)s')

    global follower_count_cache
    follower_count_cache = load_follower_count_cache_from_file(cache_file)

    following_usernames = []
    followers_usernames = []
    use_api = instagrapi_available and not args.json

    if args.json or not instagrapi_available:
        use_api = False
        logging.info("Using JSON files for input (or fallback to JSON due to missing instagrapi).")
        followers_usernames = safe_load_json_followers(followers_file)
        following_usernames = safe_load_json_following(following_file, 'relationships_following')

    else: # API Mode
        logging.info("Using Instagram API for input (default).")
        global USERNAME_INSTAGRAM, PASSWORD_INSTAGRAM
        USERNAME_INSTAGRAM = args.username
        PASSWORD_INSTAGRAM = args.password

        cl = Client()
        try:
            if USERNAME_INSTAGRAM and PASSWORD_INSTAGRAM:
                logging.info("Attempting API login with provided credentials.")
                cl.login(USERNAME_INSTAGRAM, PASSWORD_INSTAGRAM)
            else:
                logging.info("No API credentials provided. Attempting API access without login (public profile).")

            user_id = cl.user_id_from_username(USERNAME_INSTAGRAM if USERNAME_INSTAGRAM else cl.get_me().username)
            following_list = cl.user_following(user_id)
            followers_list = cl.user_followers(user_id)

            following_usernames = [user.username for user in following_list.values()]
            followers_usernames = [user.username for user in followers_list.values()]

        except Exception as auth_error:
            logging.error(f"Instagram API authentication/access error: {auth_error}")
            print(f"\nERROR: Instagram API access failed: {auth_error}")
            print("If using API mode (default), ensure:")
            print("  - Credentials are correct (if provided).")
            print("  - Two-factor auth is disabled/handled.")
            print("  - Instagram isn't blocking requests (try later).")
            print("Alternatively, use --json option to use exported JSON files (no API).")
            sys.exit(1)


    logging.info(f"Loaded {len(followers_usernames)} followers and {len(following_usernames)} following.")
    non_reciprocal_usernames = set(following_usernames) - set(followers_usernames)
    logging.info(f"Found {len(non_reciprocal_usernames)} non-reciprocal accounts.")
    print("")
    print(f"Loaded {len(followers_usernames)} followers and {len(following_usernames)} following. Found {len(non_reciprocal_usernames)} non-reciprocal accounts.")
    print("")


    result_list = []
    total_users = len(non_reciprocal_usernames)
    processed_users_count = 0

    cl_api_mode = cl if use_api else None


    for username in non_reciprocal_usernames:
        processed_users_count += 1
        percentage_complete = (processed_users_count / total_users) * 100

        operation_text = f"Processing: {username}"
        operation_text_length = len(operation_text)

        print(operation_text, end="")
        update_progress_bar(percentage_complete, operation_text_length)
        print("")

        follower_count, cache_hit = fetch_follower_count_from_api(username, cl_api_mode)


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

    logging.info("Final filtered list:")
    print("\nResult List:")
    for user in sorted(result_list):
        print(user)

    save_follower_count_cache_to_file(cache_file, follower_count_cache)
    save_result_list_to_file(result_file, result_list)


if __name__ == '__main__':
    main()
