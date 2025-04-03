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
        
        # Launch Chrome with more options for stability
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
            "--safebrowsing-disable-auto-update"
        ])
        
        print("Chrome launched with remote debugging enabled.")
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
    # Optimized version using set comprehension
    unique_digits = len({d for d in str(number)})
    required_digits = int(os.getenv('REQUIRED_DISTINCT_DIGITS', 3))
    return unique_digits == required_digits

def get_speed_settings():
    """Get speed-related settings from environment variables"""
    try:
        search_speed = float(os.getenv('SEARCH_SPEED', '1.0'))
        min_wait = float(os.getenv('MIN_WAIT_TIME', '0.5'))
        max_wait = float(os.getenv('MAX_WAIT_TIME', '3.0'))
        
        # Ensure values are within reasonable limits
        search_speed = max(0.1, min(10.0, search_speed))
        min_wait = max(0.1, min(5.0, min_wait))
        max_wait = max(min_wait, min(10.0, max_wait))
        
        return {
            'speed': search_speed,
            'min_wait': min_wait,
            'max_wait': max_wait
        }
    except ValueError:
        return {
            'speed': 1.0,
            'min_wait': 0.5,
            'max_wait': 3.0
        }

def get_adjusted_wait_time(base_time):
    """Adjust wait time based on speed settings"""
    settings = get_speed_settings()
    adjusted_time = base_time / settings['speed']
    return max(settings['min_wait'], min(settings['max_wait'], adjusted_time))

def find_number_with_three_distinct_digits(playwright, browser=None, page=None, max_attempts=None, found_numbers=None):
    """Find a number with exactly three distinct digits. If browser and page are provided, use them instead of creating new ones."""
    if found_numbers is None:
        found_numbers = set()
        
    try:
        if not browser:
            print("Connecting to Chrome...")
            browser = playwright.chromium.connect_over_cdp(f"http://localhost:{os.getenv('CHROME_DEBUG_PORT', 9222)}")
            print("Connected to Chrome successfully!")
        
        if not page:
            # Get all pages and find the one with the Eight URL
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
                print("Please make sure you're on the Eight number selection page")
                return None, (browser, page)
                
            page = found_page
        
        attempts = 0
        if max_attempts is None:
            max_attempts = int(os.getenv('MAX_SEARCH_ATTEMPTS', '1'))
        
        required_digits = int(os.getenv('REQUIRED_DISTINCT_DIGITS', 3))
        
        # Cache selectors for faster access
        button_container_selector = 'div[orientation="horizontal"]'
        button_selector = f'{button_container_selector} button'
        show_more_selector = 'span:has-text("Show more numbers")'
        
        # Get speed-adjusted timeouts
        base_timeout = int(os.getenv('PAGE_TIMEOUT', 15000))
        base_load_wait = int(os.getenv('LOAD_WAIT_TIME', 1))
        
        timeout = int(get_adjusted_wait_time(base_timeout) * 1000)  # Convert to milliseconds
        load_wait = get_adjusted_wait_time(base_load_wait)
        
        while attempts < max_attempts:
            attempts += 1
            
            try:
                # Wait for buttons with adjusted timeout
                container = page.wait_for_selector(button_container_selector, timeout=timeout)
                if not container:
                    continue
                
                # Get all buttons at once and process them
                buttons = page.query_selector_all(button_selector)
                
                # Process all visible numbers at once
                numbers = []
                for button in buttons:
                    try:
                        markdown_div = button.query_selector('div.markdown')
                        if markdown_div:
                            number = int(markdown_div.inner_text())
                            if number not in found_numbers:  # Only add numbers we haven't seen before
                                numbers.append(number)
                    except:
                        continue
                
                # Check all numbers in one batch
                for number in numbers:
                    if has_exactly_three_distinct_digits(number) and number not in found_numbers:
                        print(f"\nFound new number with exactly {required_digits} distinct digits: {number}")
                        found_numbers.add(number)  # Add to our set of found numbers
                        return number, (browser, page)
                
                # Click "Show more numbers" if available
                show_more_button = page.query_selector(show_more_selector)
                if show_more_button:
                    show_more_button.click()
                    # Use adjusted wait time
                    time.sleep(load_wait)
                else:
                    print("\nNo more numbers available to check")
                    return None, (browser, page)
                    
            except Exception as e:
                print(f"Error during search: {e}")
                continue
        
        return None, (browser, page)
        
    except Exception as e:
        print(f"Error connecting to browser: {e}")
        return None, (None, None)

if __name__ == "__main__":
    # First, launch Chrome with remote debugging
    if launch_chrome_with_debugging():
        # Then run the main script
        found_numbers = set()  # Use a set to track unique numbers
        current_max_attempts = int(os.getenv('MAX_SEARCH_ATTEMPTS', '1'))
        required_digits = int(os.getenv('REQUIRED_DISTINCT_DIGITS', 3))
        
        print(f"\nSearching for numbers with exactly {required_digits} distinct digits...")
        
        # Create a single Playwright instance for the entire session
        with sync_playwright() as playwright:
            browser = None
            page = None
            
            while True:
                # First search with current max_attempts
                result, (browser, page) = find_number_with_three_distinct_digits(playwright, browser, page, current_max_attempts, found_numbers)
                if result:
                    print(f"\nFound numbers so far: {sorted(list(found_numbers))}")
                
                # Ask if user wants to continue searching
                print("\nDo you want to continue searching? (y/n)")
                if input().lower() != 'y':
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
                
                # Keep searching until we find the requested number of numbers or run out of attempts
                remaining_searches = current_max_attempts
                while remaining_searches > 0:
                    result, (browser, page) = find_number_with_three_distinct_digits(playwright, browser, page, remaining_searches, found_numbers)
                    if result:
                        print(f"\nFound numbers so far: {sorted(list(found_numbers))}")
                        remaining_searches -= 1
                    else:
                        print("\nNo more numbers found in this batch.")
                        break
                        
                print(f"\nCompleted searching for {current_max_attempts} more numbers.")
                print(f"Total unique numbers found: {len(found_numbers)}")
            
            # Close the browser connection
            if browser:
                try:
                    browser.close()
                except:
                    pass
        
        if found_numbers:
            print(f"\nAll found numbers: {sorted(list(found_numbers))}")
        else:
            print(f"No numbers with exactly {os.getenv('REQUIRED_DISTINCT_DIGITS', 3)} distinct digits found")
    else:
        print("Failed to launch Chrome with remote debugging. Please follow the manual instructions.")
