---
description: Chaîne Atelier — devis → acompte → solde → encaissement → relance (Dolibarr)
argument-hint: "[--client <nom>]"
---
Lance la chaîne : `proposal-builder` → `devis-facture-fr` (devis, facture d'acompte, facture de solde dans Dolibarr)
→ `credit-desk` → `invoice-chase` → `quote-followup` pour les devis sans réponse.
Lecture Dolibarr libre, écriture sur validation à chaque étape. Réponds en français.
