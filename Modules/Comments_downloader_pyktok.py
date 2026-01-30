# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os
import random
import time
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pyktok as pyk


def _sanitize_folder_name(name: str) -> str:
    """Sanitize nombre for folder in Windows/Linux."""
    if not name:
        return "unknown_profile"
    name = name.strip().lower().replace(" ", "_")
    forbidden = '<>:"/\\|?*'
    for ch in forbidden:
        name = name.replace(ch, "")
    return name or "unknown_profile"


def _safe_load_json(path: str, default: Any) -> Any:
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _safe_write_json(path: str, data: Any) -> None:
    tmp = path + ".tmp"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def _index_by_video_id(items: Iterable[dict]) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for it in items:
        if isinstance(it, dict):
            vid = str(it.get("video_id") or "")
            if vid:
                out[vid] = it
    return out


def _extract_username(videos: List[dict]) -> str:
    username = "unknown_profile"
    if videos and isinstance(videos[0], dict):
        username = videos[0].get("username") or videos[0].get("Username") or username
    return _sanitize_folder_name(str(username))


def _video_dir(profile_root: str, video_id: str) -> str:
    return os.path.join(profile_root, str(video_id))


def _should_skip_video(profile_root: str, video_id: str) -> bool:
    """If the folder of the video does not exist, we can not save comments there."""
    return not os.path.isdir(_video_dir(profile_root, video_id))


def _download_comments_for_url(
    url: str,
    video_dir: str,
    comment_count: int,
    headless: bool,
    browser: str,
    soft_retry: bool,
) -> Tuple[bool, Optional[str]]:
    """Download comments in video_dir using pyktok.

    Returns (ok, error_message).
    """
    prev_cwd = os.getcwd()
    try:
        os.makedirs(video_dir, exist_ok=True)
        os.chdir(video_dir)

        # Cookies from a real browser.
        pyk.specify_browser(browser)

        pyk.save_tiktok_comments(
            url,
            filename="comments",
            comment_count=int(comment_count),
            save_comments=True,
            return_comments=False,
            headless=bool(headless),
        )
        return True, None
    except Exception as e:
        if soft_retry:
            # Soft retrial: refresh cookies and wait a little.
            try:
                pyk.specify_browser(browser)
            except Exception:
                pass
            time.sleep(random.uniform(15, 35))
            try:
                pyk.save_tiktok_comments(
                    url,
                    filename="comments",
                    comment_count=int(comment_count),
                    save_comments=True,
                    return_comments=False,
                    headless=bool(headless),
                )
                return True, None
            except Exception as e2:
                return False, str(e2)
        return False, str(e)
    finally:
        try:
            os.chdir(prev_cwd)
        except Exception:
            pass


def download_comments_from_clean_json(
    clean_json_path: str,
    output_root: str = "DOWNLOADED_VIDEOS",
    comment_count: int = 300,
    headless: bool = False,
    browser: str = "firefox",
    sleep_range_seconds: Tuple[int, int] = (30, 60),
    long_sleep_every: int = 3,
    long_sleep_range_seconds: Tuple[int, int] = (60, 120),
    soft_retry: bool = True,
) -> Dict[str, Any]:
    """Download comments based on a *_clean.json file (downloaded videos).

    3 cases: 
    - If there is NOT any <username>_comentarios_no_descargados.json file, either 
      it has never been tried or everything is OK. 
      In this case, it is calculated as "clean.json videos" - "downloaded_comments.json"
    - If not_downloaded_comments exists: just try with those.
      - If not_downloaded_comments is empty at the end of the execution, it is deleted.

    Returns a summary-dict with counters.
    """

    videos: List[dict] = _safe_load_json(clean_json_path, default=[])
    if not isinstance(videos, list) or not videos:
        return {
            "ok": False,
            "reason": "clean_json empty or invalid",
            "attempted": 0,
            "downloaded": 0,
            "failed": 0,
        }

    username = _extract_username(videos)
    profile_root = os.path.join(output_root, username)
    os.makedirs(profile_root, exist_ok=True)

    downloaded_json = os.path.join(profile_root, f"{username}_comentarios_descargados.json")
    failed_json = os.path.join(profile_root, f"{username}_comentarios_no_descargados.json")

    downloaded_list: List[dict] = _safe_load_json(downloaded_json, default=[])
    failed_list: List[dict] = _safe_load_json(failed_json, default=[])

    # Normaliza (por si hay duplicados)
    downloaded_by_id = _index_by_video_id(downloaded_list)
    failed_by_id = _index_by_video_id(failed_list)
    clean_by_id = _index_by_video_id(videos)

    # Decide qué intentar:
    if os.path.exists(failed_json) and failed_by_id:
        # Caso 2: hubo intento previo y quedan pendientes
        todo_by_id = {vid: failed_by_id[vid] for vid in list(failed_by_id.keys()) if vid in clean_by_id}
    else:
        # Caso 1 o 3: o nunca se intentó, o ya está todo. 
        # Caso 3: ya está todo descargado (no hay pendientes)
        if os.path.exists(downloaded_json) and not os.path.exists(failed_json):
            return {"status": "all_done", "downloaded": 0, "failed": 0}
        # Caso 1: Nunca se intentó
        else:
            todo_by_id = {vid: item for vid, item in clean_by_id.items() if vid not in downloaded_by_id}

    attempted = 0
    downloaded_now = 0
    failed_now = 0

    # Itera de forma estable
    todo_items = list(todo_by_id.items())

    for idx, (video_id, item) in enumerate(todo_items, start=1):
        url = item.get("video_url") or item.get("Video_url")
        if not url or not isinstance(url, str) or not url.startswith("http"):
            # URL inválida => marcamos como fallido
            failed_by_id[video_id] = item
            continue

        if _should_skip_video(profile_root, video_id):
            # No existe carpeta del vídeo (no está descargado o no coincide la estructura)
            failed_by_id[video_id] = item
            continue

        attempted += 1
        video_dir = _video_dir(profile_root, video_id)
        
        print(f"\n[{idx}/{len(todo_items)}] 🎥 Video {video_id} → intentando descargar comentarios...")
        
        ok, err = _download_comments_for_url(
            url=url,
            video_dir=video_dir,
            comment_count=comment_count,
            headless=headless,
            browser=browser,
            soft_retry=soft_retry,
        )

        if ok:
            downloaded_now += 1
            downloaded_by_id[video_id] = item
            # Si estaba en failed, lo quitamos
            failed_by_id.pop(video_id, None)
            print(f"    ✅ Comentarios descargados correctamente")
        else:
            failed_now += 1
            # Guardamos el item en failed (sin machacar metadatos previos)
            failed_by_id[video_id] = item
            print(f"    ❌ Error al descargar comentarios")
            if err:
                print(f"       Motivo: {err}")

        # Sleep anti-rate-limit (similar a tu script)
        if long_sleep_every and (idx % long_sleep_every == 0):
            time.sleep(random.uniform(*long_sleep_range_seconds))
        else:
            time.sleep(random.uniform(*sleep_range_seconds))

    # Persistimos los JSONs
    downloaded_out = list(downloaded_by_id.values())
    failed_out = list(failed_by_id.values())

    if downloaded_out:
        _safe_write_json(downloaded_json, downloaded_out)
    else:
        # Si no hay nada descargado aún, no forzamos crear el archivo
        # (pero si existe, lo dejamos tal cual)
        if os.path.exists(downloaded_json):
            _safe_write_json(downloaded_json, downloaded_out)

    if failed_out:
        _safe_write_json(failed_json, failed_out)
    else:
        # Caso 3: si queda vacío, eliminar
        if os.path.exists(failed_json):
            try:
                os.remove(failed_json)
            except Exception:
                # fallback: lo dejamos vacío
                _safe_write_json(failed_json, failed_out)

    return {
        "ok": True,
        "username": username,
        "profile_root": profile_root,
        "attempted": attempted,
        "downloaded": downloaded_now,
        "failed": failed_now,
        "remaining_failed": len(failed_out),
        "downloaded_total": len(downloaded_out),
        "clean_total": len(clean_by_id),
        "downloaded_json": downloaded_json,
        "failed_json": failed_json,
    }
