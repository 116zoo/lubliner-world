#!/usr/bin/env python3
"""Envoie les variantes sociales de content/magazine/social/ vers Postiz, en BROUILLON uniquement.

Rien n'est publié ni programmé : un humain relit et valide dans l'interface Postiz.

Variables d'environnement :
  POSTIZ_API_KEY  clé d'API de l'organisation (jamais écrite dans un fichier)
  POSTIZ_URL      défaut http://localhost:4007

Usage : python3 integrations/postiz/push_drafts.py [--dry-run]
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOCIAL = ROOT / "content" / "magazine" / "social"
URL = os.environ.get("POSTIZ_URL", "http://localhost:4007").rstrip("/")
KEY = os.environ.get("POSTIZ_API_KEY", "")
# fichier -> (mot-clé d'identifiant d'intégration Postiz, réglages spécifiques)
CHANNELS = {
    "instagram.md": ("instagram", {"post_type": "post"}),
    "linkedin.md": ("linkedin", {}),
    "facebook.md": ("facebook", {}),
    "gmb.md": ("gmb", {"topicType": "STANDARD"}),
}


def call(path, payload=None):
    req = urllib.request.Request(
        f"{URL}/api/public/v1/{path}",
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Authorization": KEY, "Content-Type": "application/json"},
        method="POST" if payload is not None else "GET",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def upload(path):
    """Téléverse une image dans Postiz (multipart) ; renvoie {id, path}."""
    boundary = "----pp" + os.urandom(8).hex()
    body = (
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
        "Content-Type: image/webp\r\n\r\n"
    ).encode() + path.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        f"{URL}/api/public/v1/upload", data=body, method="POST",
        headers={"Authorization": KEY, "Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        res = json.load(r)
    return {"id": res["id"], "path": res["path"]}


def main():
    dry = "--dry-run" in sys.argv
    if not KEY and not dry:
        sys.exit("POSTIZ_API_KEY manquante (voir brancher-mcp.sh ou Paramètres > Public API dans Postiz).")
    integrations = [] if dry else call("integrations")
    image = None if dry else upload(ROOT / "assets" / "salle-polyvalente.webp")
    for name, (needle, settings) in CHANNELS.items():
        content = (SOCIAL / name).read_text(encoding="utf-8").strip()
        target = next((i for i in integrations if needle in (i.get("identifier") or "").lower()), None)
        if dry or target is None:
            print(f"[{name}] {'dry-run' if dry else 'aucun compte ' + needle + ' connecté dans Postiz'} ({len(content)} car.)")
            continue
        res = call(
            "posts",
            {
                "type": "draft",
                "shortLink": False,
                "date": datetime.now(timezone.utc).isoformat(),
                "tags": [],
                "posts": [
                    {"integration": {"id": target["id"]}, "settings": settings, "value": [{"content": content, "image": [image] if image else []}]}
                ],
            },
        )
        print(f"[{name}] brouillon créé pour {target.get('name', needle)}: {json.dumps(res)[:120]}")


if __name__ == "__main__":
    main()
