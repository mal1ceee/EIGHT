# Eight Mobile Number Finder

A Python script that automatically searches for phone numbers with a specific number of distinct digits on the Eight mobile number selection page.

## Features

- Automatically detects and launches Chrome with remote debugging enabled
- Searches for phone numbers with exactly N distinct digits (configurable)
- Automatically clicks "Show more numbers" to load additional options
- Configurable settings through environment variables
- Detailed logging of the search process

## Prerequisites

- Python 3.7 or higher
- Google Chrome browser
- pip (Python package installer)

## Installation

1. Clone this repository or download the files
2. Install the required packages:
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
   - Search through available numbers
   - Click "Show more numbers" if needed
   - Stop when it finds a number with the required number of distinct digits
   - Display the found number

## Example

If you want to find a number with exactly 4 distinct digits:
1. Edit the `.env` file:
```env
REQUIRED_DISTINCT_DIGITS=4
```

2. Run the script as described above

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