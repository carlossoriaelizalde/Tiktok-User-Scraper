# -*- coding: utf-8 -*-
"""
Created on Wed Jan 28 18:28:39 2026

@author: carlo
"""
"""
import os
import json
import time
import pyktok as pyk

def process_json_file(json_path, output_root="DOWNLOADED_VIDEOS", sleep_time=5):

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    username = "unknown_profile"
    if isinstance(data, list) and len(data) > 0:
        username = data[0].get("username") or data[0].get("Username") or username
        username = username.strip().lower().replace(" ", "_")

    profile_root = os.path.join(output_root, username)
    os.makedirs(profile_root, exist_ok=True)

    valid_videos = []
    discarded_videos = []

    for i, video in enumerate(data, start=1):
        url = video.get("video_url") or video.get("Video_url")
        video_id = video.get("video_id")

        if not video_id:
            print("[SKIP] video_id inválido")
            discarded_videos.append(video)
            continue

        if not url or not url.startswith("http"):
            print(f"[SKIP] URL inválida: {video_id}")
            discarded_videos.append(video)
            continue

        print(f"[{i}] Descargando {video_id}")

        video_dir = os.path.join(profile_root, video_id)
        os.makedirs(video_dir, exist_ok=True)

        try:
            pyk.save_tiktok(
                url,
                True,
                os.path.join(video_dir, "video_data.csv")
            )
            valid_videos.append(video)
            time.sleep(sleep_time)

        except Exception as e:
            print(f"[FAIL] {video_id}: {e}")
            discarded_videos.append(video)

            try:
                for f in os.listdir(video_dir):
                    os.remove(os.path.join(video_dir, f))
                os.rmdir(video_dir)
            except:
                pass

            time.sleep(2)

    base_name = os.path.splitext(os.path.basename(json_path))[0]
    clean_json = os.path.join(profile_root, f"{base_name}_clean.json")
    discarded_json = os.path.join(profile_root, f"{base_name}_discarded.json")

    with open(clean_json, "w", encoding="utf-8") as f:
        json.dump(valid_videos, f, ensure_ascii=False, indent=2)

    with open(discarded_json, "w", encoding="utf-8") as f:
        json.dump(discarded_videos, f, ensure_ascii=False, indent=2)

    print("\nResumen:")
    print(f"✔ Vídeos descargados: {len(valid_videos)}")
    print(f"✘ Vídeos descartados: {len(discarded_videos)}")

"""
import os
import json
import time
import pyktok as pyk


def _sanitize_folder_name(name: str) -> str:
    """Sanitiza nombre para carpeta en Windows."""
    if not name:
        return "unknown_profile"
    name = name.strip().lower().replace(" ", "_")
    # Quita caracteres problemáticos en Windows
    forbidden = '<>:"/\\|?*'
    for ch in forbidden:
        name = name.replace(ch, "")
    return name or "unknown_profile"


def process_json_file(json_path, output_root="DOWNLOADED_VIDEOS", sleep_time=5):
    # Carga JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Detecta username
    username = "unknown_profile"
    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        username = data[0].get("username") or data[0].get("Username") or username
    username = _sanitize_folder_name(username)

    # DOWNLOADED_VIDEOS/<username>
    profile_root = os.path.join(output_root, username)
    os.makedirs(profile_root, exist_ok=True)

    valid_videos = []
    discarded_videos = []

    # Para que pyktok guarde donde queremos
    prev_cwd_global = os.getcwd()

    for i, video in enumerate(data, start=1):
        if not isinstance(video, dict):
            print(f"[SKIP] Item no válido (no es dict) en posición {i}")
            discarded_videos.append(video)
            continue

        url = video.get("video_url") or video.get("Video_url")
        video_id = video.get("video_id")

        if not video_id:
            print("[SKIP] video_id inválido")
            discarded_videos.append(video)
            continue

        if not url or not isinstance(url, str) or not url.startswith("http"):
            print(f"[SKIP] URL inválida: {video_id} -> {url}")
            discarded_videos.append(video)
            continue

        print(f"[{i}] Descargando {video_id}")

        video_dir = os.path.join(profile_root, str(video_id))
        os.makedirs(video_dir, exist_ok=True)

        try:
            # CLAVE: pyktok guarda el mp4 en el CWD
            os.chdir(video_dir)

            # Al estar ya dentro del directorio del vídeo, el CSV se queda ahí también
            pyk.save_tiktok(url, True, "video_data.csv")

            valid_videos.append(video)
            time.sleep(sleep_time)

        except Exception as e:
            print(f"[FAIL] {video_id}: {e}")
            discarded_videos.append(video)

            # Limpieza (borra lo que se haya creado a medias)
            try:
                for fname in os.listdir(video_dir):
                    fpath = os.path.join(video_dir, fname)
                    if os.path.isfile(fpath):
                        os.remove(fpath)
                # Intenta borrar la carpeta si quedó vacía
                if not os.listdir(video_dir):
                    os.rmdir(video_dir)
            except:
                pass

            time.sleep(2)

        finally:
            # Siempre volvemos al directorio original del proceso
            try:
                os.chdir(prev_cwd_global)
            except:
                pass

    # Guarda JSON limpio y descartado dentro de la carpeta del perfil
    base_name = os.path.splitext(os.path.basename(json_path))[0]
    clean_json = os.path.join(profile_root, f"{base_name}_clean.json")
    discarded_json = os.path.join(profile_root, f"{base_name}_discarded.json")

    with open(clean_json, "w", encoding="utf-8") as f:
        json.dump(valid_videos, f, ensure_ascii=False, indent=2)

    with open(discarded_json, "w", encoding="utf-8") as f:
        json.dump(discarded_videos, f, ensure_ascii=False, indent=2)

    print("\nResumen:")
    print(f"✔ Vídeos descargados: {len(valid_videos)}")
    print(f"✘ Vídeos descartados: {len(discarded_videos)}")
    print(f"📁 Guardado en: {profile_root}")