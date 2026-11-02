#!/usr/bin/env python3
"""Tableau de bord CEO Dolibarr — lecture seule (GET uniquement).

Variables d'environnement requises :
  DOLIBARR_URL      ex. https://extrapp.fr
  DOLIBARR_API_KEY  clé API (jamais écrite dans un fichier)

Sortie : dashboard-ceo.html (page autonome, graphiques SVG, sans ressource externe).
"""
import html
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone

BASE = os.environ.get("DOLIBARR_URL", "").rstrip("/")
KEY = os.environ.get("DOLIBARR_API_KEY", "")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard-ceo.html")
LAST_MONTHS = 12


def get_all(path, **params):
    """GET paginé ; renvoie la liste complète (liste vide si 404 = aucun résultat)."""
    rows, page = [], 0
    while True:
        q = urllib.parse.urlencode({**params, "limit": 100, "page": page})
        req = urllib.request.Request(
            f"{BASE}/api/index.php/{path}?{q}", headers={"DOLAPIKEY": KEY}, method="GET"
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                chunk = json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                break
            raise
        if not chunk:
            break
        rows.extend(chunk)
        if len(chunk) < 100:
            break
        page += 1
    return rows


def f(x):
    try:
        return float(x or 0)
    except (TypeError, ValueError):
        return 0.0


def status(row):
    for k in ("statut", "status", "fk_statut"):
        if row.get(k) not in (None, ""):
            return int(row[k])
    return -1


def month(ts):
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m")
    except (TypeError, ValueError):
        return "inconnu"


def eur(x):
    return f"{x:,.0f} €".replace(",", " ")


def short(x):
    return f"{x/1000:.0f} k" if abs(x) >= 1000 else f"{x:.0f}"


def last_months(n):
    now = datetime.now(timezone.utc)
    y, m = now.year, now.month
    out = []
    for _ in range(n):
        out.append(f"{y:04d}-{m:02d}")
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    return out[::-1]


def bar_chart(items, cls="c1", fmt=lambda v: f"{v:.0f}"):
    """Histogramme vertical SVG. items = [(libellé, valeur)]."""
    w, h, pad_l, pad_b, pad_t = 640, 220, 8, 34, 22
    n = max(len(items), 1)
    vmax = max([v for _, v in items] + [1])
    slot = (w - pad_l * 2) / n
    bw = slot * 0.62
    parts = [f'<svg viewBox="0 0 {w} {h}" role="img" class="chart">']
    parts.append(f'<line x1="0" y1="{h-pad_b}" x2="{w}" y2="{h-pad_b}" class="axis"/>')
    for i, (lab, v) in enumerate(items):
        bh = (h - pad_b - pad_t) * v / vmax
        x = pad_l + i * slot + (slot - bw) / 2
        y = h - pad_b - bh
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="3" class="{cls}"/>')
        if v:
            parts.append(f'<text x="{x+bw/2:.1f}" y="{y-5:.1f}" text-anchor="middle" class="val">{html.escape(fmt(v))}</text>')
        parts.append(f'<text x="{x+bw/2:.1f}" y="{h-pad_b+16}" text-anchor="middle" class="lab">{html.escape(lab[-5:] if len(lab)==7 else lab)}</text>')
    parts.append("</svg>")
    return "".join(parts)


def hbars(items):
    """Barres horizontales. items = [(libellé, valeur, classe)]."""
    w, row, lab_w = 640, 34, 120
    h = row * len(items) + 8
    vmax = max([v for _, v, _ in items] + [1])
    parts = [f'<svg viewBox="0 0 {w} {h}" role="img" class="chart">']
    for i, (lab, v, cls) in enumerate(items):
        y = 4 + i * row
        bw = (w - lab_w - 70) * v / vmax
        parts.append(f'<text x="0" y="{y+19}" class="lab2">{html.escape(lab)}</text>')
        parts.append(f'<rect x="{lab_w}" y="{y+4}" width="{max(bw,2):.1f}" height="22" rx="3" class="{cls}"/>')
        parts.append(f'<text x="{lab_w+max(bw,2)+8:.1f}" y="{y+20}" class="val">{v:.0f}</text>')
    parts.append("</svg>")
    return "".join(parts)


def donut(parts_in, center):
    """Anneau SVG. parts_in = [(libellé, valeur, classe)]."""
    total = sum(v for _, v, _ in parts_in) or 1
    r, c = 62, 2 * 3.14159265 * 62
    out = ['<svg viewBox="0 0 330 160" role="img" class="chart donut">']
    off = 0.0
    for lab, v, cls in parts_in:
        ln = c * v / total
        out.append(
            f'<circle cx="80" cy="80" r="{r}" fill="none" stroke-width="24" class="{cls}s" '
            f'stroke-dasharray="{ln:.1f} {c-ln:.1f}" stroke-dashoffset="{-off:.1f}" transform="rotate(-90 80 80)"/>'
        )
        off += ln
    out.append(f'<text x="80" y="86" text-anchor="middle" class="big">{html.escape(center)}</text>')
    for i, (lab, v, cls) in enumerate(parts_in):
        y = 50 + i * 28
        out.append(f'<rect x="170" y="{y-11}" width="14" height="14" rx="3" class="{cls}"/>')
        out.append(f'<text x="192" y="{y}" class="lab2">{html.escape(lab)} ({v:.0f})</text>')
    out.append("</svg>")
    return "".join(out)


def main():
    if not BASE or not KEY:
        sys.exit("DOLIBARR_URL et DOLIBARR_API_KEY doivent être définies dans l'environnement.")

    tiers = get_all("thirdparties", sortfield="t.rowid", sortorder="ASC")
    devis = get_all("proposals", sortfield="t.rowid", sortorder="ASC")
    factures = get_all("invoices", sortfield="t.rowid", sortorder="ASC")
    months = last_months(LAST_MONTHS)

    # --- Prospection : client = 2 (prospect), 1 (client), 3 (les deux)
    pros_m = defaultdict(int)
    n_pros = n_cli = 0
    for t in tiers:
        c = int(t.get("client") or 0)
        if c in (2, 3):
            n_pros += 1
            pros_m[month(t.get("date_creation"))] += 1
        if c in (1, 3):
            n_cli += 1
    hors_periode = sum(v for k, v in pros_m.items() if k not in months)

    # --- Devis : 0 brouillon, 1 ouvert, 2 signé, 3 refusé, 4 facturé
    libelle = {0: "Brouillon", 1: "Ouvert", 2: "Signé", 3: "Refusé", 4: "Facturé"}
    cls_dev = {0: "c3", 1: "c2", 2: "c1", 3: "c4", 4: "c1"}
    n_s, amt_s = defaultdict(int), defaultdict(float)
    dev_m = defaultdict(int)
    for d in devis:
        s = status(d)
        n_s[s] += 1
        amt_s[s] += f(d.get("total_ht"))
        if s >= 1:
            dev_m[month(d.get("date"))] += 1
    emis = sum(v for s, v in n_s.items() if s >= 1)
    signes = n_s[2] + n_s[4]
    taux = signes / emis * 100 if emis else 0

    # --- Factures émises (validées, hors avoirs)
    fac_n, fac_ht = defaultdict(int), defaultdict(float)
    n_fac = n_avoir = n_paye = 0
    reste = encaisse = 0.0
    for fa in factures:
        if status(fa) < 1:
            continue
        if int(fa.get("type") or 0) == 2:
            n_avoir += 1
            continue
        m = month(fa.get("date"))
        fac_n[m] += 1
        fac_ht[m] += f(fa.get("total_ht"))
        n_fac += 1
        paye_ttc = f(fa.get("totalpaid"))
        encaisse += paye_ttc
        if int(fa.get("paye") or 0) == 1:
            n_paye += 1
        else:
            reste += f(fa.get("total_ttc")) - paye_ttc

    def card(label, value, sub=""):
        s = f'<div class="sub">{html.escape(sub)}</div>' if sub else ""
        return f'<div class="card"><div class="v">{html.escape(str(value))}</div><div>{html.escape(label)}</div>{s}</div>'

    page = f"""<!doctype html><html lang="fr"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tableau de bord CEO</title>
<style>
:root{{--ink:#17211F;--paper:#F4F3EE;--raised:#fff;--line:#DEDCD1;--c1:#0B6B5C;--c2:#B9781F;--c3:#8A948F;--c4:#B3392C;--muted:#5d6864}}
@media(prefers-color-scheme:dark){{:root{{--ink:#F4F3EE;--paper:#17211F;--raised:#22302D;--line:#35443F;--c1:#3FB59E;--c2:#E0A24A;--c3:#7E8A85;--c4:#E27B6E;--muted:#a3ada8}}}}
body{{font:16px system-ui,sans-serif;margin:0;padding:16px;background:var(--paper);color:var(--ink);max-width:980px;margin-inline:auto}}
h1{{font-size:1.4rem;margin:.2em 0}} h2{{margin:2rem 0 .6rem;font-size:1.1rem;border-bottom:1px solid var(--line);padding-bottom:4px}}
h3{{font-size:.95rem;margin:1rem 0 .2rem;color:var(--muted);font-weight:600}}
.cards{{display:flex;flex-wrap:wrap;gap:12px}}
.card{{background:var(--raised);padding:12px 16px;border-radius:8px;min-width:150px;flex:1}}
.v{{font-size:1.6rem;font-weight:600;color:var(--c1)}} .sub{{font-size:.8rem;color:var(--muted)}}
.panel{{background:var(--raised);border-radius:8px;padding:8px 12px;margin-top:8px}}
.chart{{width:100%;height:auto;display:block}} .donut{{max-width:420px}}
.c1{{fill:var(--c1)}}.c2{{fill:var(--c2)}}.c3{{fill:var(--c3)}}.c4{{fill:var(--c4)}}
.c1s{{stroke:var(--c1)}}.c2s{{stroke:var(--c2)}}.c3s{{stroke:var(--c3)}}.c4s{{stroke:var(--c4)}}
.axis{{stroke:var(--line);stroke-width:1}}
.val{{font-size:11px;fill:var(--ink)}} .lab{{font-size:11px;fill:var(--muted)}} .lab2{{font-size:13px;fill:var(--ink)}} .big{{font-size:20px;font-weight:600;fill:var(--ink)}}
.note{{font-size:.85rem;color:var(--muted)}}
</style>
<h1>Atelier des Abbesses : tableau de bord CEO</h1>
<p class="note">Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')} · source : Dolibarr (lecture seule) · {LAST_MONTHS} derniers mois</p>

<h2>Prospection</h2>
<div class="cards">{card('Prospects', n_pros)}{card('Clients', n_cli)}</div>
<h3>Prospects créés par mois</h3>
<div class="panel">{bar_chart([(m, pros_m.get(m, 0)) for m in months])}</div>
<p class="note">{hors_periode} prospects datent de plus de {LAST_MONTHS} mois ou n'ont pas de date (import probable) : ils sont hors du graphique.</p>

<h2>Devis</h2>
<div class="cards">{card('Devis émis', emis, 'hors brouillons')}{card('Signés ou facturés', signes)}{card('Taux de transformation', f'{taux:.0f} %', 'signés / émis')}{card('Brouillons', n_s[0], eur(amt_s[0]) + ' HT')}</div>
<h3>Devis par statut (nombre)</h3>
<div class="panel">{hbars([(libelle[s], n_s[s], cls_dev[s]) for s in sorted(libelle)])}</div>
<h3>Devis émis par mois</h3>
<div class="panel">{bar_chart([(m, dev_m.get(m, 0)) for m in months], 'c2')}</div>
<h3>Montant HT par statut</h3>
<div class="panel">{hbars([(libelle[s], amt_s[s] / 1000, cls_dev[s]) for s in sorted(libelle) if s])}</div>
<p class="note">Montants en milliers d'euros HT (brouillons exclus du graphique).</p>

<h2>Factures émises</h2>
<div class="cards">{card('Factures émises', n_fac)}{card('Payées', n_paye)}{card('Avoirs', n_avoir)}{card('Reste à encaisser', eur(reste), 'TTC')}{card('Déjà encaissé', eur(encaisse), 'TTC')}</div>
<h3>Nombre de factures par mois</h3>
<div class="panel">{bar_chart([(m, fac_n.get(m, 0)) for m in months])}</div>
<h3>Chiffre d'affaires facturé HT par mois</h3>
<div class="panel">{bar_chart([(m, fac_ht.get(m, 0.0)) for m in months], 'c1', short)}</div>
<h3>Paiement des factures</h3>
<div class="panel">{donut([('Payées', n_paye, 'c1'), ('À encaisser', n_fac - n_paye, 'c2')], f'{n_fac}')}</div>
</html>"""
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(page)
    print(f"OK : {OUT}  ({len(tiers)} tiers, {len(devis)} devis, {len(factures)} factures lus)")


if __name__ == "__main__":
    main()
