from playwright.sync_api import sync_playwright
import time
import os
import subprocess
import requests
from dotenv import load_dotenv
import psutil
import shutil

# Load environment variables
load_dotenv()

def kill_chrome_processes():
    """Kill all existing Chrome processes"""
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], capture_output=True)
        else:  # Linux/Mac
            subprocess.run(['pkill', 'chrome'], capture_output=True)
        time.sleep(2)  # Wait for processes to close
    except Exception as e:
        print(f"Warning: Could not kill Chrome processes: {e}")

def wait_for_chrome_debugger():
    print("Waiting for Chrome debugger to be ready...")
    max_attempts = int(os.getenv('MAX_DEBUG_ATTEMPTS', 10))
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"http://localhost:{os.getenv('CHROME_DEBUG_PORT', 9222)}/json/version")
            if response.status_code == 200:
                print("Chrome debugger is ready!")
                return True
        except:
            print(f"Attempt {attempt + 1}/{max_attempts}: Waiting for Chrome debugger...")
            time.sleep(int(os.getenv('DEBUG_WAIT_TIME', 2)))
    return False

def find_chrome_path():
    """Find Chrome installation path on Windows"""
    possible_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe")
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Found Chrome at: {path}")
            return path
            
    print("Chrome not found in common installation paths.")
    return None

def launch_chrome_with_debugging():
    # Kill existing Chrome processes
    kill_chrome_processes()
    
    # Find Chrome installation path
    chrome_path = find_chrome_path()
    if not chrome_path:
        print("Please manually launch Chrome with remote debugging enabled:")
        print("1. Open Command Prompt as Administrator")
        print("2. Navigate to your Chrome installation directory")
        print(f"3. Run: chrome.exe --remote-debugging-port={os.getenv('CHROME_DEBUG_PORT', 9222)}")
        return False
    
    try:
        # Create unique user data directory
        user_data_dir = os.path.join(os.getcwd(), "chrome-debug-profile")
        if os.path.exists(user_data_dir):
            shutil.rmtree(user_data_dir)
        
        # Launch Chrome with more options for stability and open eight.com.sg
        subprocess.Popen([
            chrome_path,
            f"--remote-debugging-port={os.getenv('CHROME_DEBUG_PORT', 9222)}",
            f"--user-data-dir={user_data_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-background-networking",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-breakpad",
            "--disable-client-side-phishing-detection",
            "--disable-default-apps",
            "--disable-dev-shm-usage",
            "--disable-extensions",
            "--disable-features=site-per-process",
            "--disable-hang-monitor",
            "--disable-ipc-flooding-protection",
            "--disable-popup-blocking",
            "--disable-prompt-on-repost",
            "--disable-renderer-backgrounding",
            "--disable-sync",
            "--disable-translate",
            "--metrics-recording-only",
            "--no-sandbox",
            "--safebrowsing-disable-auto-update",
            "https://www.eight.com.sg/"  # Add the URL to open
        ])
        
        print("Chrome launched with remote debugging enabled and navigating to eight.com.sg")
        print("\nPlease complete the following steps:")
        print(f"1. Navigate to {os.getenv('TARGET_URL', 'https://account.eight.com.sg/activation/choose-number')}")
        print("2. Complete any human verification if needed")
        print("3. Get to the page with the numbers")
        print("4. Press Enter when ready to start the script")
        input()
        
        # Wait for Chrome debugger with better error handling
        if not wait_for_chrome_debugger():
            print("\nTroubleshooting steps:")
            print("1. Close all Chrome windows manually")
            print("2. Check Task Manager and end all Chrome processes")
            print("3. Delete the chrome-debug-profile folder")
            print("4. Try running the script again")
            return False
            
        return True
    except Exception as e:
        print(f"Error launching Chrome: {e}")
        print("\nTroubleshooting steps:")
        print("1. Make sure you have administrator privileges")
        print("2. Close all Chrome windows")
        print("3. Check Task Manager and end all Chrome processes")
        print("4. Try running the script again")
        return False

def has_exactly_three_distinct_digits(number):
    # Convert number to string and count unique digits
    unique_digits = len(set(str(number)))
    required_digits = int(os.getenv('REQUIRED_DISTINCT_DIGITS', 3))
    return unique_digits == required_digits

def find_number_with_three_distinct_digits(browser=None, page=None, max_attempts=None):
    """Find a number with exactly three distinct digits. If browser and page are provided, use them instead of creating new ones."""
    try:
        if not browser:
            print("Connecting to Chrome...")
            # Try to connect multiple times if needed
            max_connect_attempts = 3
            browser = None
            
            for attempt in range(max_connect_attempts):
                try:
                    with sync_playwright() as p:
                        browser = p.chromium.connect_over_cdp(f"http://localhost:{os.getenv('CHROME_DEBUG_PORT', 9222)}")
                        print("Connected to Chrome successfully!")
                        break
                except Exception as e:
                    if attempt < max_connect_attempts - 1:
                        print(f"Connection attempt {attempt + 1} failed: {e}")
                        print("Retrying in 2 seconds...")
                        time.sleep(2)
                    else:
                        print("Failed to connect to Chrome after multiple attempts")
                        print("\nTroubleshooting steps:")
                        print("1. Make sure Chrome is running with remote debugging enabled")
                        print("2. Check if the debugging port is correct")
                        print("3. Try closing and reopening Chrome")
                        print("4. Run the script again")
                        return None, (None, None)
        
        if not page:
            # Get all pages and find the one with the Eight URL
            print("Looking for the Eight number selection page...")
            contexts = browser.contexts
            target_url = os.getenv('TARGET_URL', 'https://account.eight.com.sg/activation/choose-number')
            found_page = None
            
            for context in contexts:
                for p in context.pages:
                    if target_url in p.url:
                        found_page = p
                        break
                if found_page:
                    break
            
            if not found_page:
                print(f"Could not find page with URL containing '{target_url}'")
                print("Please make sure you're on the Eight number selection page")
                return None, (browser, None)
                
            page = found_page
            print(f"Found the correct page: {page.url}")
            
            # Wait for page to be fully loaded with better error handling
            print("Waiting for page to be fully loaded...")
            try:
                page.wait_for_load_state("networkidle", timeout=int(os.getenv('PAGE_TIMEOUT', 60000)))
            except Exception as e:
                print(f"Warning: Page load timeout: {e}")
                print("Continuing anyway...")
        
        attempts = 0
        # Use provided max_attempts or read from .env with proper error handling
        if max_attempts is None:
            try:
                max_attempts = int(os.getenv('MAX_SEARCH_ATTEMPTS', '1'))
                print(f"Maximum search attempts set to: {max_attempts}")
            except ValueError:
                print("Warning: Invalid MAX_SEARCH_ATTEMPTS value in .env file. Using default value of 1.")
                max_attempts = 1
        
        required_digits = int(os.getenv('REQUIRED_DISTINCT_DIGITS', 3))
        
        while attempts < max_attempts:
            attempts += 1
            print(f"\nAttempt {attempts}/{max_attempts}: Checking current numbers...")
            
            # Wait for the buttons to be visible with increased timeout
            print("Waiting for number buttons to appear...")
            try:
                # First check if the container exists
                container = page.wait_for_selector('div[orientation="horizontal"]', timeout=int(os.getenv('PAGE_TIMEOUT', 60000)))
                if not container:
                    print("Could not find the button container!")
                    continue
                    
                # Then wait for buttons
                buttons = page.wait_for_selector('div[orientation="horizontal"] button', timeout=int(os.getenv('PAGE_TIMEOUT', 60000)))
                if not buttons:
                    print("Could not find any number buttons!")
                    continue
                    
                print("Found the button container and buttons!")
            except Exception as e:
                print(f"Error waiting for buttons: {e}")
                print("Current page content:")
                print(page.content())
                continue
            
            # Get all buttons containing numbers
            buttons = page.query_selector_all('div[orientation="horizontal"] button')
            print(f"Found {len(buttons)} number buttons")
            
            # Check each button for numbers with exactly the required number of distinct digits
            for button in buttons:
                try:
                    # Get the number from the markdown div inside the button
                    markdown_div = button.query_selector('div.markdown')
                    if markdown_div:
                        number_text = markdown_div.inner_text()
                        number = int(number_text)
                        print(f"\nChecking number: {number}")
                        
                        # Check if the number has exactly the required number of distinct digits
                        if has_exactly_three_distinct_digits(number):
                            print(f"\nFound number with exactly {required_digits} distinct digits: {number}")
                            print("Success! Found a suitable number.")
                            return number, (browser, page)
                except Exception as e:
                    print(f"Error processing button: {e}")
                    continue
            
            # If no number with required distinct digits found, click "Show more numbers"
            try:
                print("\nLooking for 'Show more numbers' button...")
                show_more_button = page.query_selector('span:has-text("Show more numbers")')
                if show_more_button:
                    print("No suitable number found. Clicking 'Show more numbers'...")
                    show_more_button.click()
                    print("Clicked 'Show more numbers'")
                    # Wait for new numbers to load
                    print("Waiting for new numbers to load...")
                    time.sleep(int(os.getenv('LOAD_WAIT_TIME', 3)))  # Increased wait time
                    # Wait for the old numbers to disappear and new ones to appear
                    page.wait_for_selector('div[orientation="horizontal"] button', timeout=int(os.getenv('PAGE_TIMEOUT', 60000)))
                else:
                    print("No more numbers available")
                    return None, (browser, page)
            except Exception as e:
                print(f"Error clicking show more button: {e}")
                return None, (browser, page)
        
        print(f"\nReached maximum attempts ({max_attempts}) without finding a suitable number")
        return None, (browser, page)
    except Exception as e:
        print(f"Error in find_number_with_three_distinct_digits: {e}")
        return None, (browser, page)

if __name__ == "__main__":
    print("\nPlease follow these steps:")
    print("1. Open Chrome with remote debugging enabled:")
    print("   - Close all Chrome windows")
    print("   - Open Command Prompt as Administrator")
    print("   - Navigate to your Chrome installation directory")
    print(f"   - Run: chrome.exe --remote-debugging-port={os.getenv('CHROME_DEBUG_PORT', 9222)}")
    print(f"2. Navigate to {os.getenv('TARGET_URL', 'https://account.eight.com.sg/activation/choose-number')}")
    print("3. Complete any human verification if needed")
    print("4. Get to the page with the numbers")
    print("5. Press Enter when ready to start the script")
    input()

    # Wait for Chrome debugger
    if not wait_for_chrome_debugger():
        print("\nTroubleshooting steps:")
        print("1. Make sure Chrome is running with remote debugging enabled")
        print("2. Check if the debugging port is correct")
        print("3. Try closing and reopening Chrome")
        print("4. Run the script again")
        exit(1)

    # Run the main script
    browser = None
    page = None
    found_numbers = []
    current_max_attempts = int(os.getenv('MAX_SEARCH_ATTEMPTS', '1'))
    required_digits = int(os.getenv('REQUIRED_DISTINCT_DIGITS', 3))
    
    print(f"\nSearching for numbers with exactly {required_digits} distinct digits...")
    
    try:
        with sync_playwright() as p:
            # Connect to the existing Chrome instance
            print("Connecting to Chrome...")
            browser = p.chromium.connect_over_cdp(f"http://localhost:{os.getenv('CHROME_DEBUG_PORT', 9222)}")
            
            # Get all pages and find the one with the Eight URL
            print("Looking for the Eight number selection page...")
            contexts = browser.contexts
            target_url = os.getenv('TARGET_URL', 'https://account.eight.com.sg/activation/choose-number')
            found_page = None
            
            for context in contexts:
                for p in context.pages:
                    if target_url in p.url:
                        found_page = p
                        break
                if found_page:
                    break
            
            if not found_page:
                print(f"Could not find page with URL containing '{target_url}'")
                print("Please make sure you're on the Eight number selection page")
            else:
                page = found_page
                print(f"Found the correct page: {page.url}")
                
                while True:
                    # Search for numbers
                    result, (browser, page) = find_number_with_three_distinct_digits(browser, page, current_max_attempts)
                    if result:
                        found_numbers.append(result)
                        print(f"\nFound numbers so far: {found_numbers}")
                        
                        # Ask if user wants to continue searching
                        print("\nDo you want to continue searching? (y/n)")
                        if input().lower() != 'y':
                            if found_numbers:
                                print(f"\nAll found numbers: {found_numbers}")
                            else:
                                print(f"No numbers with exactly {os.getenv('REQUIRED_DISTINCT_DIGITS', 3)} distinct digits found")
                            break
                        
                        # Ask how many more numbers to search for
                        print("\nHow many more numbers would you like to search for? (Enter a number or press Enter for default)")
                        try:
                            additional_searches = input().strip()
                            if additional_searches:
                                current_max_attempts = int(additional_searches)
                                print(f"Will search for {current_max_attempts} more numbers")
                            else:
                                current_max_attempts = int(os.getenv('MAX_SEARCH_ATTEMPTS', '1'))
                                print(f"Using default of {current_max_attempts} more searches")
                        except ValueError:
                            print("Invalid input. Using default number of searches.")
                            current_max_attempts = int(os.getenv('MAX_SEARCH_ATTEMPTS', '1'))
                            
                        # Click "Show more numbers" and continue searching
                        try:
                            print("\nLooking for 'Show more numbers' button...")
                            show_more_button = page.query_selector('span:has-text("Show more numbers")')
                            if show_more_button:
                                print("Clicking 'Show more numbers' to continue searching...")
                                show_more_button.click()
                                print("Clicked 'Show more numbers'")
                                # Wait for new numbers to load
                                print("Waiting for new numbers to load...")
                                time.sleep(int(os.getenv('LOAD_WAIT_TIME', 3)))
                                # Wait for the old numbers to disappear and new ones to appear
                                page.wait_for_selector('div[orientation="horizontal"] button', timeout=int(os.getenv('PAGE_TIMEOUT', 60000)))
                            else:
                                print("No more numbers available")
                                if found_numbers:
                                    print(f"\nAll found numbers: {found_numbers}")
                                else:
                                    print(f"No numbers with exactly {os.getenv('REQUIRED_DISTINCT_DIGITS', 3)} distinct digits found")
                                break
                        except Exception as e:
                            print(f"Error clicking show more button: {e}")
                            if found_numbers:
                                print(f"\nAll found numbers: {found_numbers}")
                            else:
                                print(f"No numbers with exactly {os.getenv('REQUIRED_DISTINCT_DIGITS', 3)} distinct digits found")
                            break
                    else:
                        print("\nNo suitable number found in this batch.")
                        if found_numbers:
                            print(f"\nAll found numbers: {found_numbers}")
                        else:
                            print(f"No numbers with exactly {os.getenv('REQUIRED_DISTINCT_DIGITS', 3)} distinct digits found")
                        break
    except Exception as e:
        print(f"An error occurred: {e}")
        if found_numbers:
            print(f"\nAll found numbers: {found_numbers}")
        else:
            print(f"No numbers with exactly {os.getenv('REQUIRED_DISTINCT_DIGITS', 3)} distinct digits found")
