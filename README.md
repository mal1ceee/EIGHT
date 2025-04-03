# Eight Mobile Number Finder

A Python script that automatically searches for phone numbers with a specific number of distinct digits on the Eight mobile number selection page.

## Features

- Automatically detects and launches Chrome with remote debugging enabled
- Searches for phone numbers with exactly N distinct digits (configurable)
- Automatically clicks "Show more numbers" to load additional options
- Configurable settings through environment variables
- Detailed logging of the search process
- Interactive search with user prompts to continue searching

## Prerequisites

- Python 3.7 or higher
- Google Chrome browser
- pip (Python package installer)

## Important Note
⚠️ **Before Running the Script**:
1. Close ALL Chrome browser windows and processes if unable to detect 
2. If you can't close Chrome, open Task Manager and:
   - Look for any "Google Chrome" processes
   - End all Chrome-related tasks
   - This ensures a clean start for the debugging session

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Install required packages:
```bash
pip install -r requirements.txt
playwright install
```

## Configuration

Create a `.env` file in the project root with the following settings:

```env
# Debug settings
CHROME_DEBUG_PORT=9222
MAX_DEBUG_ATTEMPTS=10
DEBUG_WAIT_TIME=2

# Script settings
MAX_SEARCH_ATTEMPTS=100
LOAD_WAIT_TIME=3
VERIFY_WAIT_TIME=5
PAGE_TIMEOUT=60000

# Target URL
TARGET_URL="https://account.eight.com.sg/activation/choose-number"

# Number settings
REQUIRED_DISTINCT_DIGITS=3
```

### Environment Variables Explained

- `CHROME_DEBUG_PORT`: Port for Chrome remote debugging
- `MAX_DEBUG_ATTEMPTS`: Number of attempts to connect to Chrome
- `DEBUG_WAIT_TIME`: Time to wait between connection attempts
- `MAX_SEARCH_ATTEMPTS`: Maximum number of times to try finding numbers
- `LOAD_WAIT_TIME`: Time to wait after clicking "Show more numbers"
- `PAGE_TIMEOUT`: Maximum time to wait for page elements
- `TARGET_URL`: The URL of the Eight number selection page
- `REQUIRED_DISTINCT_DIGITS`: Number of distinct digits required in the phone number

## Usage

1. Run the script:
```bash
python bryan.py
```

2. Follow the prompts:
   - The script will automatically detect and launch Chrome with remote debugging enabled
   - Navigate to the Eight number selection page
   - Complete any human verification if required
   - Press Enter when ready to start the search

3. The script will:
   - Show how many distinct digits it's searching for
   - Search through available numbers
   - Click "Show more numbers" if needed
   - Stop when it finds a number with the required number of distinct digits
   - Ask if you want to continue searching
   - Ask how many more numbers to search for if you want to continue

4. When prompted to continue:
   - Type 'y' and press Enter to continue searching
   - Type 'n' and press Enter to stop searching and see all found numbers

5. When asked how many more numbers to search for:
   - Enter a number (e.g., 5) to search for that many additional numbers
   - Press Enter without typing a number to use the default value (1)
   - The script will search for the specified number of additional numbers

## Interactive Search Example

Here's an example of how the interactive search works:

```
Searching for numbers with exactly 3 distinct digits...

Found a suitable number: 112233
Total numbers found so far: [112233]

Do you want to continue searching? (y/n)
y

How many more numbers would you like to search for?
3

Found a suitable number: 122333
Found a suitable number: 111223
No more suitable numbers found in this batch.

All found numbers: [112233, 122333, 111223]
```

## Examples

### Example 1: Finding numbers with exactly 3 distinct digits
If you want to find a number with exactly 3 distinct digits (e.g., 112233, 122333, 111223):
1. Edit the `.env` file:
```env
REQUIRED_DISTINCT_DIGITS=3
```

2. Run the script as described above

### Example 2: Finding numbers with exactly 4 distinct digits
If you want to find a number with exactly 4 distinct digits (e.g., 11223344, 12334455):
1. Edit the `.env` file:
```env
REQUIRED_DISTINCT_DIGITS=4
```

2. Run the script as described above

## How the Search Works

The script looks for numbers that have exactly the specified number of distinct digits. For example:

- With `REQUIRED_DISTINCT_DIGITS=3`:
  - 112233 would be suitable (has exactly 3 distinct digits: 1,2,3)
  - 123456 would not be suitable (has 6 distinct digits)
  - 111111 would not be suitable (has only 1 distinct digit)

- With `REQUIRED_DISTINCT_DIGITS=4`:
  - 11223344 would be suitable (has exactly 4 distinct digits: 1,2,3,4)
  - 123456 would not be suitable (has 6 distinct digits)
  - 111222 would not be suitable (has only 2 distinct digits)

## Troubleshooting

1. If Chrome doesn't launch:
   - Make sure Chrome is installed in one of the standard locations
   - The script will automatically check common installation paths
   - If Chrome is installed in a custom location, you'll need to launch it manually

2. If the script can't find the page:
   - Make sure you're on the correct URL
   - Check if the `TARGET_URL` in `.env` matches your current page

3. If the script times out:
   - Increase `PAGE_TIMEOUT` in `.env`
   - Check your internet connection
   - Make sure the page is fully loaded before pressing Enter

## License

This project is open source and available under the MIT License. 