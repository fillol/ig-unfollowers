# Instagram Unfollowers

Script to filter a list of Instagram users who **do not reciprocate the "follow"**, based on data exported from Instagram in JSON format. Additionally, it retrieves the **follower count** of each non-reciprocal user by scraping their web profile and allows for verifying their relevance based on a **maximum follower threshold**.

## Main Features:
- **Persistent Cache**: Saves retrieved follower counts in a JSON file to reduce future requests to Instagram.
- **Error Handling and Retry**: Retry mechanism with exponential backoff to ensure reliability.
- **Progress Bar**: Clear visual feedback on the process advancement.
- **Optional Verbose Logging**: Option to activate detailed logging with `-v` or `--verbose`.
- **Clean Output**: Clear printing of results on the terminal and saving to a text file.
- **Request Optimization**: Minimizes the number of requests to Instagram to speed up execution.
- **Follower Threshold Filter**: Allows setting a maximum follower limit to include a user in the filtered list.

## Prerequisites

- **Python 3.x** installed.
- **Instagram JSON Files**: `followers.json` and `following.json`, exported from Instagram account settings.

## How to Obtain Instagram JSON Files

To use this script, you need to download your data from Instagram, specifically requesting the "Followers and following" information in JSON format. Here's how to do it:

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

After downloading, you will receive a ZIP archive. Extract this archive, and you will find the `followers.json` and `following.json` files, which you should place in the same directory as the `unfollowers.py` script.

## Script Usage

1. **Preparation**: Save the code as `unfollowers.py` and place `followers.json` and `following.json` in the same directory.
2. **Execution**:
   ```bash
   python unfollowers.py
   ```
3. **Verbose Option (Detailed Logging)**:
   ```bash
   python unfollowers.py -v
   ```
4. **Script Output**:
   - Progress bar for each processed user.
   - Log messages with processing information.
   - List of non-reciprocal users printed on screen and saved to `filtered_list.txt`.
   - Cache updated in `follower_count_cache.json`.

## Input JSON Files

- `followers.json`: Contains the list of your followers.
- `following.json`: Contains the list of users you follow.

## Output Files

- `filtered_list.txt`: List of non-reciprocal usernames with followers below the defined threshold.
- `follower_count_cache.json`: Cache of follower counts to optimize future executions.

## Customization and Parameters

- **Follower Threshold**: Modify the `THRESHOLD` variable at the beginning of the script:
   ```python
   THRESHOLD = 10000  # Modifiable based on preferences
   ```
- **File Names**: Defined with constants at the beginning of the script:
   ```python
   CACHE_FILE_PATH = 'follower_count_cache.json'
   RESULT_FILE_PATH = 'filtered_list.txt'
   followers_file = 'followers.json'
   following_file = 'following.json'
   ```
- **Logging**: To activate `INFO` level, run with `-v` or `--verbose`.

## Important Considerations

- **Changes to Instagram pages** may require script updates.
- **Avoid excessive requests** to prevent violating Instagram's terms of service.
- **Use of cache** is highly recommended to improve performance.
