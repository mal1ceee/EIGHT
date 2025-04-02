from playwright.sync_api import sync_playwright
import time
import os
import subprocess
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
    # Find Chrome installation path
    chrome_path = find_chrome_path()
    if not chrome_path:
        print("Please manually launch Chrome with remote debugging enabled:")
        print("1. Open Command Prompt as Administrator")
        print("2. Navigate to your Chrome installation directory")
        print(f"3. Run: chrome.exe --remote-debugging-port={os.getenv('CHROME_DEBUG_PORT', 9222)}")
        return False
    
    try:
        # Launch Chrome with remote debugging
        subprocess.Popen([chrome_path, f"--remote-debugging-port={os.getenv('CHROME_DEBUG_PORT', 9222)}"])
        print("Chrome launched with remote debugging enabled.")
        print("Please complete the following steps:")
        print(f"1. Navigate to {os.getenv('TARGET_URL', 'https://account.eight.com.sg/activation/choose-number')}")
        print("2. Complete any human verification if needed")
        print("3. Get to the page with the numbers")
        print("4. Press Enter when ready to start the script")
        input()
        
        # Wait for Chrome debugger to be ready
        if not wait_for_chrome_debugger():
            print("Failed to connect to Chrome debugger. Please make sure Chrome is running with remote debugging enabled.")
            return False
            
        return True
    except Exception as e:
        print(f"Error launching Chrome: {e}")
        return False

def has_exactly_three_distinct_digits(number):
    # Convert number to string and count unique digits
    unique_digits = len(set(str(number)))
    required_digits = int(os.getenv('REQUIRED_DISTINCT_DIGITS', 3))
    return unique_digits == required_digits

def find_number_with_three_distinct_digits():
    with sync_playwright() as p:
        try:
            print("Connecting to Chrome...")
            # Connect to the already running browser
            browser = p.chromium.connect_over_cdp(f"http://localhost:{os.getenv('CHROME_DEBUG_PORT', 9222)}")
            print("Connected to Chrome successfully!")
            
            # Get all pages and find the one with the Eight URL
            print("Looking for the Eight number selection page...")
            contexts = browser.contexts
            target_url = os.getenv('TARGET_URL', 'https://account.eight.com.sg/activation/choose-number')
            found_page = None
            
            for context in contexts:
                for page in context.pages:
                    if target_url in page.url:
                        found_page = page
                        break
                if found_page:
                    break
            
            if not found_page:
                print(f"Could not find page with URL containing '{target_url}'")
                print("Please make sure you're on the Eight number selection page")
                browser.close()
                return None
                
            page = found_page
            print(f"Found the correct page: {page.url}")
            
            # Wait for page to be fully loaded
            print("Waiting for page to be fully loaded...")
            page.wait_for_load_state("networkidle", timeout=int(os.getenv('PAGE_TIMEOUT', 60000)))
            
            attempts = 0
            max_attempts = int(os.getenv('MAX_SEARCH_ATTEMPTS', 100))  # Prevent infinite loop
            required_digits = int(os.getenv('REQUIRED_DISTINCT_DIGITS', 3))
            
            while attempts < max_attempts:
                attempts += 1
                print(f"\nAttempt {attempts}: Checking current numbers...")
                
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
                            print(f"Checking number: {number}")
                            
                            # Check if the number has exactly the required number of distinct digits
                            if has_exactly_three_distinct_digits(number):
                                print(f"Found number with exactly {required_digits} distinct digits: {number}")
                                print("Success! Found a suitable number.")
                                browser.close()
                                return number
                    except Exception as e:
                        print(f"Error processing button: {e}")
                        continue
                
                # If no number with required distinct digits found, click "Show more numbers"
                try:
                    print("Looking for 'Show more numbers' button...")
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
                        browser.close()
                        return None
                except Exception as e:
                    print(f"Error clicking show more button: {e}")
                    browser.close()
                    return None
            
            print(f"Reached maximum attempts ({max_attempts}) without finding a suitable number")
            browser.close()
            return None
        except Exception as e:
            print(f"Error connecting to browser: {e}")
            return None

if __name__ == "__main__":
    # First, launch Chrome with remote debugging
    if launch_chrome_with_debugging():
        # Then run the main script
        result = find_number_with_three_distinct_digits()
        if result:
            print(f"Successfully found number with {os.getenv('REQUIRED_DISTINCT_DIGITS', 3)} distinct digits: {result}")
        else:
            print(f"No number with exactly {os.getenv('REQUIRED_DISTINCT_DIGITS', 3)} distinct digits found")
    else:
        print("Failed to launch Chrome with remote debugging. Please follow the manual instructions.")
