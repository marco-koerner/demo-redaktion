"""Holt Titel, Datum, Link und Anriss der letzten 14 Tage aus festen Feeds.

Ohne KI, nur Standardbibliothek. Schreibt lagebild/eingang.md.
Scheitert ein Feed, steht das in der Datei; der Lauf geht weiter.
"""

import datetime as dt
import html
import re
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path

FEEDS = {
    "Wissenschaftskommunikation.de": "https://www.wissenschaftskommunikation.de/feed/",
    "Blog von Jan-Martin Wiarda": "https://www.jmwiarda.de/feed/",
    "CHE Centrum für Hochschulentwicklung": "https://www.che.de/feed/",
}
TAGE = 14
JE_FEED = 8
ANRISS = 280


def text(el, tag):
    t = el.find(tag)
    return (t.text or "").strip() if t is not None else ""


def bereinigt(s):
    s = re.sub(r"<[^>]+>", " ", html.unescape(s))
    s = re.sub(r"\s+", " ", s).strip()
    return s[:ANRISS] + ("…" if len(s) > ANRISS else "")


def main():
    grenze = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=TAGE)
    zeilen = ["# Eingang", "", f"Stand: {dt.date.today():%d.%m.%Y}, letzte {TAGE} Tage.", ""]
    for name, url in FEEDS.items():
        zeilen += [f"## {name}", ""]
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "demo-redaktion/1.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                wurzel = ET.fromstring(r.read())
            n = 0
            for item in wurzel.iter("item"):
                try:
                    datum = parsedate_to_datetime(text(item, "pubDate"))
                except (TypeError, ValueError):
                    continue
                if datum < grenze:
                    continue
                zeilen += [f"- **{bereinigt(text(item, 'title'))}** ({datum:%d.%m.%Y}) {text(item, 'link')}",
                           f"  {bereinigt(text(item, 'description'))}"]
                n += 1
                if n >= JE_FEED:
                    break
            if n == 0:
                zeilen.append("- nichts Neues")
        except Exception as e:  # noqa: BLE001
            zeilen.append(f"- Feed nicht lesbar: {e}")
        zeilen.append("")
    Path("lagebild/eingang.md").write_text("\n".join(zeilen), encoding="utf-8")
    print("\n".join(zeilen))


if __name__ == "__main__":
    main()
