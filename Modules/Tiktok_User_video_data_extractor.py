from datetime import datetime
import sys
import time
from camoufox.sync_api import Camoufox
import humanize
from rich import print
import json
import sys
import os

folder = os.path.dirname(os.path.realpath(__file__))

results = []

identifier_codes = set()

def get_videos(user_item,video_id):
    vid_url = 'https://www.tiktok.com/@{}/video/{}'
    print(user_item.get("statsV2", {}))
    return  {
            'video_id': video_id,
            'video_url' : vid_url.format(user_item.get('author').get('uniqueId'),user_item.get('id')),
            'createTime' : humanize.naturalday(datetime.fromtimestamp( user_item.get('createTime'))),
            'description': user_item.get('desc'),
            'user_id': user_item.get('author').get('id'),
            'username': user_item.get('author').get('uniqueId'),
            'verified':user_item.get('author').get('verified'),
            'privateAccount':user_item.get('author').get('privateAccount'),
            'userbio':user_item.get('author').get('signature'),
            'collectCount':user_item.get('stats').get('collectCount'),
            'likeCount':user_item.get('stats').get('diggCount'),
            'shareCount':user_item.get('stats').get('shareCount'),
            'commentCount':user_item.get('stats').get('commentCount'),
            'playCount':user_item.get('stats').get('playCount'),
            'repostCount':user_item.get('statsV2').get('repostCount'),
            'followingCountUser':user_item.get('authorStatsV2').get('followingCount'),
            'followerCountUser':user_item.get('authorStatsV2').get('followerCount'),
            'heartCountUser':user_item.get('authorStatsV2').get('heartCount'),
            'videoCountUser':user_item.get('authorStatsV2').get('videoCount'),
            'diggUserCount':user_item.get('authorStatsV2').get('diggCount'),
            'friendCountUser':user_item.get('authorStatsV2').get('friendCount')
        }


def get_json(response):
    all_data = []
    try:
        if not response or response.status != 200:
            return        
        if 'api/post/item_list/' in response.url:
            data = response.json()
            if data:
                for user_item in data.get('itemList'):
                    video_id = user_item.get('id')
                    if video_id not in identifier_codes:
                        identifier_codes.add(video_id)
                        all_data.append(get_videos(user_item,video_id))
            else:
                print('No json data found')   
        if all_data:  
            results.extend(all_data)
            
    except ValueError as e:
        print(f"JSON parsing error for {response.url.split('?')[0]}: {e}")
    except AttributeError as e:
        print(f"Response attribute error for {response.url.split('?')[0]}: {e}")
    except TypeError as e:
        print(f"Type error processing response from {response.url.split('?')[0]}: {e}")
    except Exception as e:
        print(f"Unexpected error processing response from {response.url.split('?')[0]}: {e}")

def write_data(data,json_file):
    """Write all data to the JSON file"""
    try:
        with open(json_file, 'w') as f:
            f.write('[\n')
            for i, item in enumerate(data):
                json_str = json.dumps(item)
                if i < len(data) - 1:
                    json_str += ','
                f.write(json_str + '\n')
            f.write(']')
    except Exception as e:
        print(f"Error writing data: {e}")

def route_intercept(route, request):
    if request.resource_type == "image" or any(ext in request.url.lower() for ext in [".png", ".jpg", ".jpeg"]):
        route.abort()
        return
    if request.resource_type == "media" or any(ext in request.url.lower() for ext in [".mp4", ".webm", ".avi"]):
        route.abort()
        return
    
    route.continue_() 


def launch_browser(Tiktok_username,VIDEO_COUNT):
    with Camoufox(os=["windows", "macos", "linux"],humanize=2.0,locale="en-US") as browser:
        page = browser.new_page()
        page.route("**/*", route_intercept)
        response_handler = lambda response: get_json(response)
        page.on("response", response_handler)
        page.goto(f'https://www.tiktok.com/@{Tiktok_username}',timeout=50000)
        page.wait_for_timeout(15000)
        captcha_button = page.locator('button#captcha_close_button')
        if captcha_button.is_visible():
            captcha_button.click()
            page.wait_for_timeout(2000)
            page.locator("//button[text()='Refresh']").click()

        while True:
            previous_count = len(identifier_codes)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            if captcha_button.is_visible():
               captcha_button.click()
               page.wait_for_timeout(2000)
               page.locator("//button[text()='Refresh']").click()

            time.sleep(15)  # Allow time for new content to load
            current_count = len(identifier_codes)

            print(f'Scraped [{current_count}] / {int(VIDEO_COUNT)} videos', end='\r', flush=True)
            if current_count >= VIDEO_COUNT:
                break
            if current_count == previous_count:
                if current_count >= VIDEO_COUNT:
                    break
                if page.evaluate("(window.innerHeight + window.scrollY) >= document.body.scrollHeight"):
                    break
        
        print(f"\n\nDone. Scraped {len(results[:VIDEO_COUNT])} videos.\n")
        page.remove_listener("response", response_handler)
        page.unroute("**/*")
        page.close()

def main(Tiktok_username,VIDEO_COUNT,output_dir="."):
    # RESET of the global state for each user
    global results, identifier_codes
    results = []
    identifier_codes = set()

    os.makedirs(os.path.join(output_dir, "DATA"), exist_ok=True)
    try:
        launch_browser(Tiktok_username, VIDEO_COUNT)
    except Exception as e:
        print(f'Error occurred : {e}')
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    finally:
        # Respect output_dir
        out_path = os.path.join(output_dir, "DATA", f"{Tiktok_username}_videos.json")
        write_data(results[:VIDEO_COUNT], out_path)
