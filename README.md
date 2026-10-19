# @andwoy Instagram-System

Wochenlauf per GitHub Actions: Themen -> Entwürfe -> Freigabe -> Posten.

## Einrichtung (einmalig)
1. Repository auf GitHub anlegen (siehe Hinweis zu "öffentlich" unten) und alle Dateien hochladen.
2. Settings -> Secrets and variables -> Actions -> "New repository secret":
   - ANTHROPIC_API_KEY
   - IG_USER_ID
   - IG_ACCESS_TOKEN
3. Settings -> Actions -> General -> Workflow permissions: "Read and write permissions".

## Ablauf
- Montags erzeugt "Wochenplan erzeugen" 3 Entwürfe in drafts/<Woche>/ (auch manuell startbar).
- Du prüfst Bild und Caption in GitHub (Ordner drafts/).
- Actions -> "Entwurf freigeben oder ablehnen" -> Run workflow: Ordner + Uhrzeit (Berlin) eintragen.
- Stündlich postet "Freigegebene Beiträge posten" alles, was freigegeben und fällig ist.

## Wichtig
- Instagram lädt Bilder per URL. Die Adresse zeigt auf raw.githubusercontent.com und
  funktioniert nur bei einem ÖFFENTLICHEN Repository. Entwürfe sind dann öffentlich lesbar.
- Reels brauchen eine Datei reel.mp4 im Entwurfsordner. Ohne sie wird das Reel übersprungen.
- Lege die Schlüssel nie ins Repository, nur in die Secrets.
