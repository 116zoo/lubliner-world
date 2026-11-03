# Personnalisation — Atelier des Abbesses

Ce dossier est la copie locale et durable : plugin `atelier-abbesses`, dérivé de small-business-fr 1.2.0-fr.1. Les skills désactivés n'y figurent pas (ils restent dans la copie en cache du plugin d'origine).

Édition adaptée le 2026-11-03. Pile du dirigeant : **Dolibarr, Postiz, Payload CMS**, Pennylane côté expert-comptable. Pas de Shopify, de stock ni d'expédition.

## Ajouté
- `skills/atelier-hub` + `/atelier` : cockpit, carte besoin → skill → outils MCP réels (Dolibarr, Postiz, Payload), garde-fous.
- `skills/onboarding-equipe` + `/onboarding` : parcours dirigeant, collaboratrice, stagiaire com.
- `/devis-a-encaissement` : chaîne devis → acompte → solde → encaissement → relance.
- `smb-router` : étape 0 bis, périmètre Atelier.

## Skills conservés (46)
Pilotage, ventes et prospection, finance et clôture, marketing et réseaux, méta (voir `skills/`).

## Désactivés (déplacés, pas supprimés)
- `skills-disabled/` : 9 skills Shopify, stock et réassort (b2b-stock-planner, inventory-planner, restock, stock-count-cutoff, customer-reorder), catalog-quote, order-intake, purchase-desk, pricing-desk, fulfillment-desk, product-compliance, inbox-manager, payroll-prep, hiring-screener, job-post-builder, micro-entrepreneur, ticket-deflector, ad-manager, pay-the-bills, renewal-watch, time-to-invoice.
- `commands-disabled/` : les commandes correspondantes.
- `.mcp.json` : retrait de `shopify`, `shopify-dev-mcp`, `sendcloud` (original dans `skills-disabled/mcp.json.original`).

## Annuler
Remettre un dossier de `skills-disabled/` dans `skills/` (idem `commands-disabled/` → `commands/`), ou réinstaller le plugin.

## Limites
Une mise à jour du plugin depuis GitHub écrase ces changements. Les références croisées dans certains skills conservés (ex. `close-month` vers `stock-count-cutoff`) pointent vers des skills désactivés : elles ne servent que pour les profils à stock.
