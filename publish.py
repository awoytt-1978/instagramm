#!/usr/bin/env python3
"""Postet freigegebene Entwürfe, deren Zeit erreicht ist, über die Instagram Graph API.
Per Cron/Scheduled Task z. B. stündlich starten.

Benötigt in .env:
  IG_USER_ID, IG_ACCESS_TOKEN        (Instagram-Business-/Creator-Konto, Meta-App)
  PUBLIC_BASE_URL                    (öffentlich erreichbare URL, unter der drafts/ liegt,
                                      denn die Graph API lädt Bild/Video per URL)
"""
import datetime as dt, json, os, sys, time
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

DRAFTS = Path(__file__).parent / "drafts"
API = os.environ.get("IG_API_HOST", "https://graph.instagram.com/v21.0")
BERLIN = ZoneInfo("Europe/Berlin")


def env(k):
    v = os.environ.get(k)
    if not v:
        sys.exit(f"Fehlt: {k} (siehe .env.example)")
    return v


def create_container(item, folder, caption):
    uid, token, base = env("IG_USER_ID"), env("IG_ACCESS_TOKEN"), env("PUBLIC_BASE_URL").rstrip("/")
    rel = folder.relative_to(DRAFTS).as_posix()
    if item["typ"] == "post":
        payload = {"image_url": f"{base}/{rel}/bild.jpg", "caption": caption}
    else:
        payload = {"media_type": "REELS", "video_url": f"{base}/{rel}/reel.mp4", "caption": caption}
    r = requests.post(f"{API}/{uid}/media", data={**payload, "access_token": token}, timeout=60)
    r.raise_for_status()
    return r.json()["id"]


def wait_ready(cid):
    token = env("IG_ACCESS_TOKEN")
    for _ in range(40):
        s = requests.get(f"{API}/{cid}", params={"fields": "status_code", "access_token": token}, timeout=30).json()
        if s.get("status_code") == "FINISHED":
            return
        if s.get("status_code") == "ERROR":
            raise RuntimeError(f"Container-Fehler: {s}")
        time.sleep(5)
    raise TimeoutError("Container nicht rechtzeitig fertig")


def main():
    now = dt.datetime.now(BERLIN)
    for p in sorted(DRAFTS.glob("*/*/entwurf.json")):
        item = json.loads(p.read_text())
        if item["status"] != "freigegeben":
            continue
        when = dt.datetime.fromisoformat(item["geplant_fuer"]).replace(tzinfo=BERLIN)
        if when > now:
            continue
        folder = p.parent
        caption = (folder / "caption.txt").read_text()
        if item["typ"] == "reel" and not (folder / "reel.mp4").exists():
            print("Übersprungen (reel.mp4 fehlt):", folder.name)
            continue
        cid = create_container(item, folder, caption)
        wait_ready(cid)
        r = requests.post(f"{API}/{env('IG_USER_ID')}/media_publish",
                          data={"creation_id": cid, "access_token": env("IG_ACCESS_TOKEN")}, timeout=60)
        r.raise_for_status()
        item["status"], item["media_id"] = "gepostet", r.json()["id"]
        p.write_text(json.dumps(item, ensure_ascii=False, indent=2))
        print("Gepostet:", folder.name, item["media_id"])


if __name__ == "__main__":
    main()
