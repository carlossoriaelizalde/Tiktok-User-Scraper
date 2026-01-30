# -*- coding: utf-8 -*-
"""
Created on Wed Jan 28 10:17:59 2026

@author: carlo
"""

import os
import sys
import random
import pyfiglet
from colorama import init, Fore
from time import sleep
from Modules import (
    Video_downloader,
    Tiktok_User_video_data_extractor,
    Video_downloader_pyktok,
    Comments_downloader_pyktok,
)
import json
import glob

init() 

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(PROJECT_ROOT, 'DATA')
DOWNLOADED_FOLDER = os.path.join(PROJECT_ROOT, 'DOWNLOADED_VIDEOS')

lg = Fore.LIGHTGREEN_EX
w = Fore.WHITE
cy = Fore.CYAN
ye = Fore.YELLOW  
r = Fore.RED
rs = Fore.RESET
colors = [lg, r, w, cy, ye]

def clear_screen():
    """Cross-platform screen clearing"""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner(tool_name=""):
    """Display the application banner with optional tool name"""
    f = pyfiglet.Figlet(font='slant', width=100)
    banner = f.renderText('TikTok Tools')
    print(f'{random.choice(colors)}{banner}{rs}')
    if tool_name:
        tool_banner = pyfiglet.Figlet(font='small', width=100)
        print(f'{cy}{tool_banner.renderText(tool_name)}{rs}')
    print(f'{r}  TikTok Video Scrapers Suite | Original Author: kev | Author: Carlos Soria Elizalde {rs}\n')

def get_valid_input(prompt, validation_func, error_message, allow_back = True):
    """Helper function to get validated input"""
    while True:
        try:
            user_input = input(prompt).strip()
            if allow_back and user_input == "0":
                return None
            if validation_func(user_input):
                return user_input
            print(f'{r}{error_message}{rs}')
        except KeyboardInterrupt:
            print(f'\n{lg}Returning to main menu...{rs}')
            sleep(1)
            return None
        
def tiktok_user_scraper_menu():
    """Handle TikTok scraper functionality (name and amount only)"""
    clear_screen()
    show_banner("User-Videos Scraper")
    
    # Get name
    username_prompt = f'{lg}Enter username to Scrape (without @ e.g.,"khaby.lame"). Enter 0 to return to main menu: {r}'
    username_validator = lambda x: 2 <= len(x) <= 24 and all(c.isalnum() or c in ['.', '_', '-'] for c in x) and not x.startswith('.') and not x.endswith('.')
    username_error = '[!] Invalid username. Please enter a valid username'
    username = get_valid_input(username_prompt, username_validator, username_error)
    if username is None:
        return
    
    # Get amount (up to 1000)
    amount_prompt = f'{lg}Enter amount of {username}`s videos to scrape (1-1000): {r}'
    amount_validator = lambda x: x.isdigit() and 1 <= int(x) <= 1000
    amount_error = '[!] Invalid amount. Please enter a number between 1 and 1000'
    amount = get_valid_input(amount_prompt, amount_validator, amount_error)
    if amount is None:
        return
    amount = int(amount)
    
    # Call the scraper function
    try:
        print(f'\n{lg}Starting TikTok scraper with parameters:')
        print(f'Name: {username}, Amount: {amount}{rs}')
        Tiktok_User_video_data_extractor.main(username, amount)  # Assuming new module takes just name and amount
        input(f'\n{lg}Press Enter to return to main menu...{rs}')
    except Exception as e:
        print(f'{r}[!] Error during scraping: {e}{rs}')
        sleep(2)

def video_downloader_menu():
    """Handle video downloader functionality"""
    clear_screen()
    show_banner("Video Downloader")
    
    # List available JSON files in Data folder (now in project root)
    os.makedirs(DATA_FOLDER, exist_ok=True)
    json_files = glob.glob(os.path.join(DATA_FOLDER, '*.json'))
    
    if not json_files:
        print(f'{r}[!] No JSON files found in Data folder{rs}')
        sleep(2)
        return
    
    print(f'{lg}Available JSON files in Data folder:{rs}')
    for i, file_path in enumerate(json_files, 1):
        file_name = os.path.basename(file_path)
        print(f'{lg}[{i}] {file_name}{rs}')
    
    # Get file selection
    file_prompt = f'\n{lg}Enter the number of the file to download (1-{len(json_files)}). Enter 0 to return to main menu: {r}'
    file_validator = lambda x: x.isdigit() and 1 <= int(x) <= len(json_files)
    file_error = f'[!] Invalid selection. Please enter a number between 1 and {len(json_files)}'
    file_choice = get_valid_input(file_prompt, file_validator, file_error)
    if file_choice is None:
        return
    
    selected_file = json_files[int(file_choice)-1]
    
    try:
        with open(selected_file, 'r', encoding = "utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            print(f'{r}[!] Invalid JSON format. Expected a list of video items.{rs}')
            sleep(2)
            return
    except json.JSONDecodeError:
        print(f'{r}[!] Invalid JSON file.{rs}')
        sleep(2)
        return
    
    try:
        print(f'\n{lg}Starting video downloader with file: {os.path.basename(selected_file)}{rs}')
        Video_downloader_pyktok.process_json_file(
            selected_file,
            output_root=os.path.join(PROJECT_ROOT, "DOWNLOADED_VIDEOS")
        )
        input(f'\n{lg}Press Enter to return to main menu...{rs}')
    except Exception as e:
        print(f'{r}[!] Error during downloading: {e}{rs}')
        sleep(2)


def comments_downloader_menu():
    """Handle comments downloader functionality (for already downloaded videos)."""
    clear_screen()
    show_banner("Comments Downloader")

    # Looks for *_clean.json inside DOWNLOADED_VIDEOS/<username>/
    os.makedirs(DOWNLOADED_FOLDER, exist_ok=True)
    clean_json_files = glob.glob(os.path.join(DOWNLOADED_FOLDER, '*', '*_clean.json'))

    if not clean_json_files:
        print(f'{r}[!] No *_clean.json files found in {DOWNLOADED_FOLDER}{rs}')
        print(f'{ye}Tip: First download videos (menu [2]) to create the *_clean.json.{rs}')
        sleep(2)
        return

    print(f'{lg}Available *_clean.json files (downloaded videos) found (WARNING: IF PARTIAL DOWNLOAD ALREADY DONE, IT WILL CONTINUE, NOT START FROM THE BEGINNING). Enter 0 to return to main menu:{rs}')
    for i, file_path in enumerate(clean_json_files, 1):
        rel = os.path.relpath(file_path, PROJECT_ROOT)
        print(f'{lg}[{i}] {rel}{rs}')

    file_prompt = f'\n{lg}Enter the number of the file to download comments (1-{len(clean_json_files)}): {r}'
    file_validator = lambda x: x.isdigit() and 1 <= int(x) <= len(clean_json_files)
    file_error = f'[!] Invalid selection. Please enter a number between 1 and {len(clean_json_files)}'
    file_choice = get_valid_input(file_prompt, file_validator, file_error)
    if file_choice is None:
        return

    selected_file = clean_json_files[int(file_choice) - 1]

    # Download comments
    try:
        print(f'\n{lg}Starting comments downloader with file: {os.path.basename(selected_file)}{rs}')
        summary = Comments_downloader_pyktok.download_comments_from_clean_json(
            selected_file,
            output_root=DOWNLOADED_FOLDER,
            comment_count=300,
            headless=False,
            browser="firefox",
        )
        
        if summary and summary.get("status") == "all_done":
            print("\n✅ Comments already downloaded for all available videos.")
            input("Press Enter to return to main menu...")
            return
        
        if not summary.get("ok"):
            print(f"{r}[!] {summary.get('reason', 'Unknown error')}{rs}")
        else:
            print(f"\n{lg}Summary ({summary.get('username')}):{rs}")
            print(f"  Tried: {summary.get('attempted')}\n  ✅ Downloaded comments: {summary.get('downloaded')}\n  ❌ Failed: {summary.get('failed')}\n  Pending: {summary.get('remaining_failed')}")
            print(f"\n{cy}Tracking:{rs}")
            print(f"  - {os.path.relpath(summary.get('downloaded_json'), PROJECT_ROOT)}")
            # failed_json may not exist if deleted
            if summary.get('remaining_failed'):
                print(f"  - {os.path.relpath(summary.get('failed_json'), PROJECT_ROOT)}")
            else:
                print(f"  - comments_not_downloaded.json empty -> deleted")

        input(f'\n{lg}Press Enter to return to main menu...{rs}')
    except Exception as e:
        print(f'{r}[!] Error during comments download: {e}{rs}')
        sleep(2)

def main_menu():
    """Display main menu and handle user input"""
    while True:
        clear_screen()
        show_banner()
        
        print(f'{lg}[1] User-Videos Scraper')
        print(f'[2] Video Downloader')
        print(f'[3] Comments Downloader')
        print(f'[4] Exit{rs}')
        
        try:
            choice = input(f'\n{lg}Enter your choice: {r}').strip()
            
            if choice == '1':
                tiktok_user_scraper_menu()
            elif choice == '2':
                video_downloader_menu()
            elif choice == '3':
                comments_downloader_menu()
            elif choice == '4':
                print(f'\n{lg}Goodbye!{rs}')
                sys.exit(0)
            else:
                print(f'{r}[!] Invalid choice{rs}')
                sleep(1)
        except KeyboardInterrupt:
            print(f'\n{lg}Goodbye!{rs}')
            sys.exit(0)

if __name__ == '__main__':
    main_menu()
