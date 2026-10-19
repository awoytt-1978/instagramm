#!/usr/bin/env python3
"""Freigabe: zeigt Entwürfe und setzt Status + Veröffentlichungszeit.

  python3 approve.py                       # Entwürfe auflisten
  python3 approve.py <ordner> 2026-10-14T18:00   # freigeben (Zeit = Europe/Berlin)
  python3 approve.py <ordner> --reject           # zurück auf 'abgelehnt'
"""
import json, sys
from pathlib import Path

DRAFTS = Path(__file__).parent / "drafts"


def all_drafts():
    return sorted(DRAFTS.glob("*/*/entwurf.json"))


def main():
    if len(sys.argv) == 1:
        for p in all_drafts():
            d = json.loads(p.read_text())
            print(f"{p.parent.relative_to(DRAFTS)}  [{d['status']}]  geplant: {d['geplant_fuer']}")
        return
    folder = DRAFTS / sys.argv[1]
    p = folder / "entwurf.json"
    d = json.loads(p.read_text())
    if sys.argv[2] == "--reject":
        d["status"], d["geplant_fuer"] = "abgelehnt", None
    else:
        d["status"], d["geplant_fuer"] = "freigegeben", sys.argv[2]
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2))
    print("OK:", folder.name, "->", d["status"], d["geplant_fuer"])


if __name__ == "__main__":
    main()
