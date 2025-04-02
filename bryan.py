from playwright.sync_api import sync_playwright
import time
import os
import subprocess
import requests
from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import threading

# Load environment variables
load_dotenv()

class StatusWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Eight Mobile Number Finder")
        self.root.geometry("600x400")
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Start button
        self.start_button = ttk.Button(
            self.main_frame,
            text="Start Search",
            command=self.start_search
        )
        self.start_button.grid(row=0, column=0, pady=5)
        
        # Status text
        self.status_text = tk.Text(self.main_frame, height=15, width=60)
        self.status_text.grid(row=1, column=0, pady=5)
        self.status_text.config(state=tk.DISABLED)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.main_frame, 
            length=400, 
            mode='determinate',
            variable=self.progress_var
        )
        self.progress_bar.grid(row=2, column=0, pady=5)
        
        # Elapsed time
        self.time_label = ttk.Label(self.main_frame, text="Elapsed Time: 00:00:00")
        self.time_label.grid(row=3, column=0, pady=5)
        
        self.start_time = datetime.now()
        self.update_time()
        self.script_thread = None
    
    def start_search(self):
        self.start_button.config(state=tk.DISABLED)
        self.script_thread = threading.Thread(target=self.run_script)
        self.script_thread.daemon = True
        self.script_thread.start()
    
    def run_script(self):
        if launch_chrome_with_debugging(self):
            result = find_number_with_three_distinct_digits(self)
            if result:
                self.update_status(f"Success! Found number with {os.getenv('REQUIRED_DISTINCT_DIGITS', '3')} distinct digits: {result}")
            else:
                self.update_status(f"No number with exactly {os.getenv('REQUIRED_DISTINCT_DIGITS', '3')} distinct digits found")
        else:
            self.update_status("Failed to launch Chrome with remote debugging")
        self.start_button.config(state=tk.NORMAL)
    
    def update_time(self):
        elapsed = datetime.now() - self.start_time
        self.time_label.config(text=f"Elapsed Time: {str(elapsed).split('.')[0]}")
        self.root.after(1000, self.update_time)
    
    def update_status(self, message):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
    
    def update_progress(self, value):
        self.progress_var.set(value)
    
    def run(self):
        self.root.mainloop()

def find_chrome_path(status_window):
    status_window.update_status("Searching for Chrome...")
    possible_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe")
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            status_window.update_status(f"Found Chrome at: {path}")
            return path
    
    status_window.update_status("Chrome not found in common locations")
    return None

def launch_chrome_with_debugging(status_window):
    chrome_path = find_chrome_path(status_window)
    if not chrome_path:
        status_window.update_status("Please launch Chrome manually with remote debugging enabled")
        status_window.update_status(f"Run: chrome.exe --remote-debugging-port={os.getenv('CHROME_DEBUG_PORT', '9222')}")
        return False
    
    try:
        # Check if Chrome is already running with debugging
        try:
            response = requests.get(f"http://localhost:{os.getenv('CHROME_DEBUG_PORT', '9222')}/json/version")
            if response.status_code == 200:
                status_window.update_status("Chrome already running with debugging")
                return True
        except requests.exceptions.ConnectionError:
            pass

        # Launch Chrome with debugging
        subprocess.Popen([
            chrome_path,
            f"--remote-debugging-port={os.getenv('CHROME_DEBUG_PORT', '9222')}",
            "--user-data-dir=chrome-debug-profile",
            "--no-first-run",
            "--no-default-browser-check"
        ], creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        status_window.update_status("Chrome launched with debugging")
        status_window.update_status("\nPlease complete these steps:")
        status_window.update_status(f"1. Navigate to {os.getenv('TARGET_URL', 'https://account.eight.com.sg/activation/choose-number')}")
        status_window.update_status("2. Complete any human verification if needed")
        status_window.update_status("3. Get to the page with the numbers")
        status_window.update_status("4. Press Enter when ready to start the script")
        input()
        
        if not wait_for_chrome_debugger(status_window):
            status_window.update_status("Failed to connect to Chrome debugger")
            return False
            
        return True
    except Exception as e:
        status_window.update_status(f"Error launching Chrome: {e}")
        return False

def wait_for_chrome_debugger(status_window):
    status_window.update_status("Waiting for Chrome debugger...")
    max_attempts = int(os.getenv('MAX_DEBUG_ATTEMPTS', '10'))
    wait_time = int(os.getenv('DEBUG_WAIT_TIME', '2'))
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"http://localhost:{os.getenv('CHROME_DEBUG_PORT', '9222')}/json/version")
            if response.status_code == 200:
                status_window.update_status("Connected to Chrome debugger")
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(wait_time)
            status_window.update_status(f"Attempt {attempt + 1}/{max_attempts}")
    
    status_window.update_status("Failed to connect to Chrome debugger")
    return False

def has_exactly_n_distinct_digits(number):
    distinct_digits = set(str(number))
    required_digits = int(os.getenv('REQUIRED_DISTINCT_DIGITS', '3'))
    return len(distinct_digits) == required_digits

def find_number_with_three_distinct_digits(status_window):
    with sync_playwright() as p:
        try:
            status_window.update_status("Connecting to Chrome browser...")
            browser = p.chromium.connect_over_cdp(f"http://localhost:{os.getenv('CHROME_DEBUG_PORT', '9222')}")
            status_window.update_status("Connected to Chrome browser")
            
            target_url = os.getenv('TARGET_URL', 'https://account.eight.com.sg/activation/choose-number')
            found_page = None
            
            status_window.update_status("Searching for target page...")
            for context in browser.contexts:
                for page in context.pages:
                    if target_url in page.url:
                        found_page = page
                        status_window.update_status(f"Found page: {page.url}")
                        break
                if found_page:
                    break
            
            if not found_page:
                status_window.update_status("Target page not found")
                browser.close()
                return None
                
            page = found_page
            status_window.update_status("Waiting for page to load...")
            page.wait_for_load_state("networkidle", timeout=int(os.getenv('PAGE_TIMEOUT', '60000')))
            status_window.update_status("Page loaded successfully")
            
            attempts = 0
            max_attempts = int(os.getenv('MAX_SEARCH_ATTEMPTS', '100'))
            required_digits = int(os.getenv('REQUIRED_DISTINCT_DIGITS', '3'))
            
            while attempts < max_attempts:
                attempts += 1
                progress_percent = int((attempts / max_attempts) * 100)
                status_window.update_status(f"Attempt {attempts}/{max_attempts} ({progress_percent}%)")
                status_window.update_progress(progress_percent)
                
                try:
                    status_window.update_status("Looking for number buttons...")
                    container = page.wait_for_selector('div.sc-iSmSVH', timeout=int(os.getenv('PAGE_TIMEOUT', '60000')))
                    if not container:
                        continue
                        
                    buttons = page.wait_for_selector('div.sc-iSmSVH button.sc-dAlyuH', timeout=int(os.getenv('PAGE_TIMEOUT', '60000')))
                    if not buttons:
                        continue
                        
                    buttons = page.query_selector_all('div.sc-iSmSVH button.sc-dAlyuH')
                    status_window.update_status(f"Found {len(buttons)} numbers to check")
                    
                    for button in buttons:
                        try:
                            markdown_div = button.query_selector('div.markdown')
                            if markdown_div:
                                number_text = markdown_div.inner_text()
                                number = int(number_text)
                                status_window.update_status(f"Checking number: {number}")
                                
                                if has_exactly_n_distinct_digits(number):
                                    status_window.update_status(f"Found matching number: {number}")
                                    browser.close()
                                    return number
                        except Exception as e:
                            continue
                    
                    # Try different selectors for the "Show more numbers" button
                    show_more_selectors = [
                        'button:has-text("Show more numbers")',
                        'span:has-text("Show more numbers")',
                        'div[data-testid="show-more-button"]',
                        'button.sc-dAlyuH:has-text("Show more numbers")'
                    ]
                    
                    show_more_button = None
                    for selector in show_more_selectors:
                        show_more_button = page.query_selector(selector)
                        if show_more_button:
                            break
                    
                    if show_more_button:
                        status_window.update_status("Loading more numbers...")
                        show_more_button.click()
                        time.sleep(int(os.getenv('LOAD_WAIT_TIME', '3')))
                        page.wait_for_selector('div.sc-iSmSVH button.sc-dAlyuH', timeout=int(os.getenv('PAGE_TIMEOUT', '60000')))
                    else:
                        status_window.update_status("No more numbers available")
                        browser.close()
                        return None
                except Exception as e:
                    status_window.update_status(f"Error during attempt {attempts}: {str(e)}")
                    continue
            
            status_window.update_status("Maximum attempts reached")
            browser.close()
            return None
        except Exception as e:
            status_window.update_status(f"Browser error: {str(e)}")
            return None

def main():
    status_window = StatusWindow()
    status_window.run()

if __name__ == "__main__":
    main()
