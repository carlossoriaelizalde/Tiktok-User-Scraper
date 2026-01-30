# -*- coding: utf-8 -*-
import os
import json
import time
import pyktok as pyk


def _sanitize_folder_name(name: str) -> str:
    """Sanitize name for folder in Windows/Linux."""
    if not name:
        return "unknown_profile"
    name = name.strip().lower().replace(" ", "_")
    # Delete problematic caracters in Windows
    forbidden = '<>:"/\\|?*'
    for ch in forbidden:
        name = name.replace(ch, "")
    return name or "unknown_profile"


def process_json_file(json_path, output_root="DOWNLOADED_VIDEOS", sleep_time=5):
    # Load JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Detect username
    username = "unknown_profile"
    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        username = data[0].get("username") or data[0].get("Username") or username
    username = _sanitize_folder_name(username)

    # DOWNLOADED_VIDEOS/<username>
    profile_root = os.path.join(output_root, username)
    os.makedirs(profile_root, exist_ok=True)

    valid_videos = []
    discarded_videos = []

    # So that pyktok saves where we want
    prev_cwd_global = os.getcwd()

    for i, video in enumerate(data, start=1):
        if not isinstance(video, dict):
            print(f"[SKIP] Invalid Item (not dict) in position {i}")
            discarded_videos.append(video)
            continue

        url = video.get("video_url") or video.get("Video_url")
        video_id = video.get("video_id")

        if not video_id:
            print("[SKIP] video_id inválido")
            discarded_videos.append(video)
            continue

        if not url or not isinstance(url, str) or not url.startswith("http"):
            print(f"[SKIP] Invalid URL: {video_id} -> {url}")
            discarded_videos.append(video)
            continue

        print(f"[{i}] Downloading {video_id}")

        video_dir = os.path.join(profile_root, str(video_id))
        os.makedirs(video_dir, exist_ok=True)

        try:
            # As pyktok saves the mp4 video in cwd.
            os.chdir(video_dir)

            # As we are already in the directory of the video, CSV remains there too.
            pyk.save_tiktok(url, True, "video_data.csv")

            valid_videos.append(video)
            time.sleep(sleep_time)

        except Exception as e:
            print(f"[FAIL] {video_id}: {e}")
            discarded_videos.append(video)

            # Clean (delete not finished objects)
            try:
                for fname in os.listdir(video_dir):
                    fpath = os.path.join(video_dir, fname)
                    if os.path.isfile(fpath):
                        os.remove(fpath)
                # Try to delete folder if empty
                if not os.listdir(video_dir):
                    os.rmdir(video_dir)
            except:
                pass

            time.sleep(2)

        finally:
            # Always go back to original directory
            try:
                os.chdir(prev_cwd_global)
            except:
                pass

    # Save "clean" and "discarded" JSON files inside the profile's folder
    base_name = os.path.splitext(os.path.basename(json_path))[0]
    clean_json = os.path.join(profile_root, f"{base_name}_clean.json")
    discarded_json = os.path.join(profile_root, f"{base_name}_discarded.json")

    with open(clean_json, "w", encoding="utf-8") as f:
        json.dump(valid_videos, f, ensure_ascii=False, indent=2)

    with open(discarded_json, "w", encoding="utf-8") as f:
        json.dump(discarded_videos, f, ensure_ascii=False, indent=2)

    print("\nResumen:")
    print(f"✔ Downloaded videos: {len(valid_videos)}")
    print(f"✘ Discarded videos: {len(discarded_videos)}")

    print(f"📁 Saved in: {profile_root}")

