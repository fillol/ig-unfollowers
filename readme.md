# Instagram Unfollowers

This script helps you filter your Instagram "following" list to identify users who **do not follow you back** (non-reciprocal follows). It now offers **two modes of operation**:

1.  **API Mode (Default)**: Leverages the **Instagram API** via the `instagrapi` library to directly fetch follower and following data, and to retrieve follower counts for filtering. This mode is generally faster and more reliable and is recommended for most users, **especially if the `instagrapi` library is installed**.
2.  **JSON Fallback Mode**: Uses **exported JSON files** from Instagram for your follower and following lists.  In this mode, **follower counts are retrieved by scraping Instagram user webpages**, **without relying on the `instagrapi` library for follower count retrieval**. This mode is intended as a **fallback option** for cases where `instagrapi` is not installed or when you prefer not to use the Instagram API directly for fetching follower counts.

## Table of Contents

1.  [Main Features](#main-features)
2.  [Prerequisites](#prerequisites)
3.  [How to Obtain Instagram JSON Files (for JSON Fallback Mode)](#how-to-obtain-instagram-json-files-for-json-fallback-mode)
4.  [Script Usage](#script-usage)
5.  [Input Files](#input-files)
6.  [Output Files](#output-files)
7.  [Customization and Parameters](#customization-and-parameters)
8.  [Important Considerations](#important-considerations)

## Main Features:

-   **Dual Mode Operation**: Choose between **API mode** (default, using `instagrapi` for direct API access) and **JSON Fallback mode** (using exported JSON files for initial data, with **webpage scraping for follower counts**).
-   **Persistent Cache**: Saves retrieved follower counts in a JSON file (`follower_count_cache.json`) to **minimize API requests (in API mode) or webpage scraping (in JSON Fallback mode)** and speed up future executions in both modes.
-   **Instagram API Integration**: Uses the `instagrapi` library for efficient and reliable data retrieval in API mode (for followers, following, and follower counts).
-   **Webpage Scraping for Follower Counts**: In **JSON Fallback mode**, the script retrieves follower counts by scraping Instagram user profile pages, allowing operation **without `instagrapi` dependency for follower count retrieval**.
-   **API Authentication (Optional)**: Supports optional Instagram username and password for API login in **API mode**, which can improve reliability and reduce rate limits, especially for private profiles or large accounts. **Not used in JSON Fallback mode**.
-   **JSON Files Support**:  Still supports exported Instagram JSON files (`followers.json`, `following.json`) for initial data loading in **JSON Fallback mode**.
-   **Follower Threshold Filter**: Allows setting a maximum follower limit (`THRESHOLD`) to filter non-reciprocal users based on their audience size.
-   **Progress Bar**: Provides clear visual feedback on the processing progress in the terminal.
-   **Verbose Logging Option**:  Enable detailed logging with `-v` or `--verbose` for debugging and more information.
-   **Clean Output**: Displays a clear list of filtered non-reciprocal users on the terminal and saves it to a text file (`filtered_list.txt`).

## Prerequisites

-   **Python 3.x** installed.
-   **`instagrapi` Python Library (Optional, for API Mode)**:  Highly recommended for **API mode** for efficient and reliable operation. Install it using: `pip install instagrapi`.  If `instagrapi` is not installed or if you use the `--json` option, the script will automatically fall back to **JSON Fallback mode**.
-   **Instagram JSON Files (Optional, for JSON Fallback Mode)**: `followers.json` and `following.json`. Only needed if you intend to use the **JSON Fallback mode** (`--json` option). See the section below on how to obtain these files.

## How to Obtain Instagram JSON Files (for JSON Fallback Mode)

While the script now defaults to using the Instagram API for a more efficient process (if `instagrapi` is available), you can still use exported JSON files for your follower and following lists with the `--json` option to force **JSON Fallback mode**.  Follow these steps to download your data from Instagram, specifically requesting the "Followers and following" information in JSON format:

1.  **Go to your Profile**:
    *   On the Instagram app, tap your profile picture in the bottom right corner to go to your profile.
2.  **Access Your Activity**:
    *   Tap the menu icon (three horizontal lines) in the top right corner.
    *   Select **Your activity**.
3.  **Download Your Information**:
    *   Scroll down to "Information you shared with Instagram" and tap **Download your information**.
    *   If you haven't entered your email address before, you'll be prompted to enter it. Then, tap **Request a download**.
    *   Choose **Select types of information** under "Select information".
    *   Scroll down and select **Followers and following**.
    *   Under "Select file options", it's crucial to configure the following:
        *   **Format**: Choose **JSON**.
        *   **Date range**: Select **All time**.
    *   Tap **Submit request**.
4.  **Download Data from Email**:
    *   Instagram will send an email with the subject "Your Instagram Data" containing a link to your data. This might take some time, potentially up to a day, but is usually faster.
    *   Open the email and click **Download data**.
    *   Follow the instructions on the Instagram website to finish downloading your information. You might need to navigate back to the "Download your information" page once it's ready.

After downloading, you will receive a ZIP archive. Extract this archive, and you will find the `followers.json` and `following.json` files. **If you plan to use the JSON Fallback mode (\`--json\` option), place these files in the same directory as the \`unfollowers.py\` script.** If you are using the default API mode, these files are not necessary.

## Script Usage

1.  **Installation**: Ensure you have Python 3.x installed.  For **API mode (default and recommended)**, it's highly recommended to install the `instagrapi` library: `pip install instagrapi`. Save the script code as `unfollowers.py`.
2.  **API Mode (Default - Recommended)**:
    *   By default, the script operates in **API mode**, leveraging `instagrapi` for efficient data retrieval.  This mode is recommended for most users and offers the best performance and data accuracy **if `instagrapi` is installed**.
    *   To run in API mode (if `instagrapi` is installed), simply execute the script without any options:
        ```bash
        python unfollowers.py
        ```
    *   **Optional API Credentials**: For improved reliability and to potentially avoid rate limits, especially with private profiles or large accounts, you can provide your Instagram username and password. This is optional but recommended for frequent use or larger accounts in API mode:
        ```bash
        python unfollowers.py -u YOUR_USERNAME -p YOUR_PASSWORD
        ```
        Replace `YOUR_USERNAME` and `YOUR_PASSWORD` with your actual Instagram credentials. Providing credentials can help avoid rate limits and access issues in API mode.

3.  **JSON Fallback Mode**:
    *   If you want to use exported JSON files for your follower and following lists **and use webpage scraping for follower counts (without relying on `instagrapi` for follower count retrieval)**, use the `--json` option. This mode is useful when `instagrapi` is not installed or if you prefer not to use the API directly for follower counts.
    *   Ensure `followers.json` and `following.json` are in the same directory as the script if you use JSON Fallback mode.
    *   To run in **JSON Fallback mode**, use the `--json` option:
        ```bash
        python unfollowers.py --json
        ```
    *   **JSON Mode with API Credentials (NOT Recommended)**:  While you *can* technically provide API credentials even in JSON mode (using `-u` and `-p` with `--json`), **it is generally NOT recommended and does not change the core operation of JSON Fallback mode**. In JSON Fallback mode, follower counts are *always* fetched via webpage scraping, regardless of whether API credentials are provided or not. Providing credentials in JSON mode will only be used for optional login attempts within the webpage scraping function, which is generally not necessary.

4.  **Verbose Option (Detailed Logging)**:
    ```bash
    python unfollowers.py -v
    python unfollowers.py --json -v
    python unfollowers.py -u YOUR_USERNAME -p YOUR_PASSWORD -v
    python unfollowers.py --json -u YOUR_USERNAME -p YOUR_PASSWORD -v
    ```
    Use the `-v` or `--verbose` flag to enable detailed logging output, which can be useful for debugging or understanding the script's operation in either API or JSON Fallback mode.

5.  **Script Output**:
    -   **Progress bar**:  Visual progress bar displayed in the terminal for each processed user.
    -   **Log messages**: Informative messages about the script's progress, mode of operation (API or JSON Fallback), cache usage, API calls (in API mode), webpage scraping (in JSON Fallback mode), and any potential issues (especially in verbose mode).
    -   **Console Output**: Summary of loaded followers and following, count of non-reciprocal users, and the final **"Result List"** of filtered usernames printed to the terminal.
    -   **`filtered_list.txt`**:  A text file created in the same directory containing the list of filtered non-reciprocal usernames (those who do not follow back and have a follower count below the `THRESHOLD`).
    -   **`follower_count_cache.json`**:  The cache file, updated with the follower counts retrieved during the script execution (either via API in API mode, or via webpage scraping in JSON Fallback mode). This file is used in subsequent runs to avoid redundant data fetching.

## Input Files

-   **Input Files**
    -   **`followers.json` (Optional, for JSON Fallback Mode)**:  JSON file containing the list of your followers, exported from Instagram. Required **only if using JSON Fallback mode (`--json` option)**.
    -   **`following.json` (Optional, for JSON Fallback Mode)**: JSON file containing the list of users you are following, exported from Instagram. Required **only if using JSON Fallback mode (`--json` option)**.

## Output Files

-   **Output Files**
    -   **`filtered_list.txt`**: Text file containing a list of non-reciprocal usernames that meet the follower count threshold.
    -   **`follower_count_cache.json`**: JSON file used as a cache to store follower counts, improving script performance over multiple runs in both API and JSON Fallback modes.

## Customization and Parameters

-   **Follower Threshold (`THRESHOLD`)**:  You can adjust the `THRESHOLD` variable defined at the beginning of the script in `unfollowers.py`:
    ```python
    THRESHOLD = 10000  # Modify this value to set your desired follower threshold
    ```
    This value determines the maximum follower count a non-reciprocal user can have to be included in the filtered list.  Non-reciprocal users with a follower count **equal to or below** this threshold will be included in the `filtered_list.txt` output.

-   **Output File Names**: You can customize the names of the output files and the cache file by modifying the following constants at the start of the script:
    ```python
    CACHE_FILE_PATH = 'follower_count_cache.json'
    RESULT_FILE_PATH = 'filtered_list.txt'
    FOLLOWER_FILE_DEFAULT = 'followers.json'    # Used in JSON Fallback mode
    FOLLOWING_FILE_DEFAULT = 'following.json'   # Used in JSON Fallback mode
    ```
    Note that `FOLLOWER_FILE_DEFAULT` and `FOLLOWING_FILE_DEFAULT` are only used in **JSON Fallback mode** to define the expected filenames for the input JSON files.

-   **Command Line Arguments**:
    *   `--json`: Forces the script to use **JSON Fallback mode**. In this mode, follower and following lists are loaded from `followers.json` and `following.json` files in the script's directory, and **follower counts are fetched by webpage scraping**.  This option is useful when `instagrapi` is not installed or if you prefer not to use the API for follower count retrieval.
    *   `-u USERNAME`, `--username USERNAME`:  Instagram username for API authentication.  **Optional and only relevant for API mode**.  Recommended for API mode to improve reliability and reduce rate limits, especially for private profiles or large accounts.  **Ignored in JSON Fallback mode**.
    *   `-p PASSWORD`, `--password PASSWORD`: Instagram password for API authentication. **Optional and only relevant for API mode**. Should be used in conjunction with `-u/--username`.  **Ignored in JSON Fallback mode**.
    *   `-v`, `--verbose`: Enables **verbose logging** output (INFO level).  Provides more detailed information about the script's execution in both API and JSON Fallback modes.

-   **Logging Verbosity**:  Run the script with the `-v` or `--verbose` flag to activate detailed logging (INFO level). Without this flag, the script runs in WARNING logging level, showing only important warnings and errors.  Verbose logging can be helpful for debugging or understanding the script's operation in detail.

## Important Considerations

-   **Instagram Page Structure Changes**:  Changes to Instagram's API or page structure could potentially require updates to the `instagrapi` library or the script itself, especially the webpage scraping logic. Keep `instagrapi` updated (if used in API mode) and be aware that webpage scraping might break if Instagram changes its website layout.
-   **API Rate Limits and Excessive Requests (API Mode)**: Be mindful of Instagram's API usage limits, especially if running in **API mode** without credentials or for large accounts. While the script uses caching to minimize requests, processing a very large number of users in rapid succession might still trigger rate limits in API mode. Using API credentials can help reduce the risk of rate limiting in API mode. Avoid running the script too frequently in short intervals, especially in API mode.
-   **Webpage Scraping Reliability (JSON Fallback Mode)**: Webpage scraping, used in **JSON Fallback mode**, is inherently less reliable than using the API. Instagram can change its website structure at any time, potentially breaking the scraping logic.  JSON Fallback mode is intended as a best-effort fallback, but API mode with `instagrapi` is generally more robust and reliable when possible.
-   **Cache Usage**: The `follower_count_cache.json` file is crucial for optimizing performance and reducing API requests (in API mode) and webpage scraping (in JSON Fallback mode). Ensure the script has write permissions in the directory to save the cache. It is highly recommended to **not delete** this cache file between script executions to benefit from faster subsequent runs in both modes.
-   **Security of Credentials (API Mode)**: If you choose to provide your Instagram username and password via command-line arguments **in API mode**, be aware of the security implications. While `instagrapi` handles credentials securely, avoid storing your password directly in scripts or sharing scripts with credentials exposed in command history. Consider using environment variables or other secure methods for managing credentials in more sensitive environments if needed, especially when using API mode with credentials. **Note that API credentials are not used in JSON Fallback mode for follower count retrieval.**
