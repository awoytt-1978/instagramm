#!/usr/bin/env python3
"""Wöchentlicher Generator: 7 Themen -> 3 Entwürfe (2 Posts + 1 Reel) in drafts/<Woche>/.

Aufruf:  python3 generate_week.py            (echte Generierung per Anthropic API)
         python3 generate_week.py --dry-run  (Beispieldaten ohne API, zum Testen)
"""
import argparse, datetime as dt, json, os, re, sys
from pathlib import Path

from render import render_post_image

ROOT = Path(__file__).parent
DRAFTS = ROOT / "drafts"
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")

ZIELGRUPPE = (
    "Healthcare-Zielgruppe mit den Bereichen: Ernährung; elektronische Musik und "
    "elektronische Tanzevents; Sport und Bewegung; Lebensweisheiten und Lebensmottos; "
    "optische, akustische, multisensorische und audiovisuelle Installationen, die zur "
    "Beruhigung und Entspannung genutzt werden."
)

PROMPT = f"""Du bist Content-Planer für den Instagram-Account @andwoy (Berlin, deutsch).
Zielgruppe: {ZIELGRUPPE}

Aufgabe: Erzeuge 7 Themen für diese Woche (bunt gemischt über die Bereiche). Wähle daraus
3 Themen für Veröffentlichungen: 2 Feed-Posts (Bild) und 1 Reel. Liefere NUR gültiges JSON:

{{"themen": ["...", "... (7 Stück)"],
  "auswahl": [
    {{"typ": "post|reel", "thema": "...", "bereich": "...",
      "titel_kurz": "max. 6 Wörter für die Grafik",
      "untertitel": "max. 12 Wörter für die Grafik",
      "caption": "deutsch, 400-900 Zeichen, mit Einstieg, Mehrwert, Call-to-Action",
      "hashtags": ["15-25 Hashtags ohne #"],
      "bildkonzept": "Beschreibung der Grafik/Bildidee (bei post)",
      "reel_skript": [{{"sekunde": "0-3", "bild": "...", "text_einblendung": "...", "ton": "..."}}]}}
  ]}}
Keine medizinischen Heilversprechen; sachlich, ruhig, einladend."""


def week_label(today=None):
    d = today or dt.date.today()
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def slugify(s):
    s = s.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:40]


def call_claude():
    import anthropic  # pip install anthropic
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=MODEL, max_tokens=4000,
        messages=[{"role": "user", "content": PROMPT}],
    )
    text = msg.content[0].text
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    return json.loads(text)


def sample():
    return {
        "themen": ["Magnesiumreiche Abendsnacks", "Ambient-Sets für den Feierabend",
                   "10 Minuten Mobility", "Lebensmotto: Langsam ist glatt", "Lichtinstallation zum Runterkommen",
                   "Clubnacht ohne Kater", "Atem-Rhythmus und Musik"],
        "auswahl": [
            {"typ": "post", "thema": "Magnesiumreiche Abendsnacks", "bereich": "Ernährung",
             "titel_kurz": "Abendsnacks für Ruhe", "untertitel": "Drei einfache Ideen mit Magnesium",
             "caption": "Beispiel-Caption (Dry-Run).", "hashtags": ["ernaehrung", "entspannung", "berlin"],
             "bildkonzept": "Hellblauer Verlauf, Schale mit Nüssen"},
            {"typ": "post", "thema": "Lebensmotto: Langsam ist glatt", "bereich": "Lebensweisheiten",
             "titel_kurz": "Langsam ist glatt", "untertitel": "Ein Motto für ruhigere Tage",
             "caption": "Beispiel-Caption (Dry-Run).", "hashtags": ["mindset", "ruhe", "andwoy"],
             "bildkonzept": "Typografie-Grafik, Pastellverlauf"},
            {"typ": "reel", "thema": "Lichtinstallation zum Runterkommen", "bereich": "Installationen",
             "titel_kurz": "Licht zum Runterkommen", "untertitel": "Audiovisuelle Ruhe",
             "caption": "Beispiel-Caption (Dry-Run).", "hashtags": ["lichtkunst", "entspannung"],
             "bildkonzept": "", "reel_skript": [{"sekunde": "0-3", "bild": "Farbflächen im Fluss",
                                                 "text_einblendung": "Atme ein", "ton": "Ambient-Pad"}]},
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    data = sample() if args.dry_run else call_claude()

    week = week_label()
    out_root = DRAFTS / week
    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "themen.json").write_text(json.dumps(data["themen"], ensure_ascii=False, indent=2))

    for i, item in enumerate(data["auswahl"], 1):
        folder = out_root / f"{i:02d}-{item['typ']}-{slugify(item['thema'])}"
        folder.mkdir(exist_ok=True)
        item["status"] = "entwurf"          # entwurf -> freigegeben -> gepostet
        item["geplant_fuer"] = None
        if item["typ"] == "post":
            render_post_image(item["titel_kurz"], item["untertitel"], item["bereich"], folder / "bild.jpg")
        (folder / "entwurf.json").write_text(json.dumps(item, ensure_ascii=False, indent=2))
        (folder / "caption.txt").write_text(
            item["caption"] + "\n\n" + " ".join("#" + h.lstrip("#") for h in item["hashtags"]))
        print("Entwurf:", folder.relative_to(ROOT))
    print(f"\nFertig. Bitte prüfen und freigeben:  python3 approve.py")


if __name__ == "__main__":
    sys.exit(main())
