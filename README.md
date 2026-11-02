# Lubliner World — tableau de bord CEO et publication Magazine

## Contenu

| Dossier / fichier | Rôle |
|---|---|
| `dolibarr_ceo.py`, `dashboard-ceo.html` | Tableau de bord CEO Dolibarr (lecture seule) |
| `content/magazine/` | Article central SEO/AEO (≈ 800 mots, H2/H3 sourcés) et variantes par canal |
| `integrations/payload/seed-magazine.ts` | Crée la catégorie « Magazine blog » et l'article **en brouillon** dans le Payload de Paris Private |
| `integrations/postiz/` | Serveur Postiz local : mode d'emploi, branchement MCP, envoi des variantes **en brouillon** |
| `.mcp.json` | Serveurs MCP Payload et Postiz (clés lues dans l'environnement, jamais écrites) |

## Chaîne de publication

1. Rédiger l'article central dans `content/magazine/` (front matter : titre, slug, méta, image + alt).
2. Dériver les variantes dans `content/magazine/social/` (Instagram, LinkedIn, Facebook, Google Business).
3. Payload (CMS) : depuis le projet Payload, `./node_modules/.bin/payload run <ce dépôt>/integrations/payload/seed-magazine.ts`.
4. Postiz : `python3 integrations/postiz/push_drafts.py --dry-run`, puis sans `--dry-run`.
5. Un humain relit et publie. Aucun script ne publie ni ne programme.

## Prérequis

- Payload : la base du projet doit tourner (`POSTGRES_URL`, port 54321 dans le projet actuel) ; vérifiez qu'elle vise la bonne base avant le seed.
- Postiz : si l'interface renvoie 502, démarrer Temporal (voir `integrations/postiz/README-instance-locale.md`).
- Copier `.env.example` vers `.env` et renseigner les clés.

## À confirmer avant publication

Capacité maximale, adresse, tarifs et équipement exact de la salle : l'article n'affirme que ce qui est visible sur la photo. Les chiffres d'études (Cornell, Human Spaces) viennent de sources secondaires, à vérifier à la source.
