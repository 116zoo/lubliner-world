---
name: onboarding-equipe
description: >
  Onboarding de l'équipe de l'Atelier des Abbesses : parcours du dirigeant, de la
  collaboratrice administrative et de la stagiaire en communication digitale.
  Dolibarr, Payload CMS, Postiz, Pennylane (pas de Shopify).
  [EN] Team onboarding for three roles: CEO, admin/sales colleague, digital comms intern.
---

> Language rule: see `shared/language.md`.

# onboarding-equipe

## Avant de commencer
1. Lis le bloc `## Business context` de la mémoire du projet. S'il est absent, lance `smb-onboard`.
2. Il n'y a **pas de Shopify** : n'utilise aucun skill `shopify-*`. La pile est Dolibarr (ERP, facturation), Payload CMS (site), Postiz (réseaux sociaux), Pennylane (côté expert-comptable).
3. Les chiffres de `reference/page-onboarding.html` datent du 3 novembre 2026. Avant de les citer, relis-les dans Dolibarr (`dashboard-ceo.html`, régénéré par `dolibarr_ceo.py`, lecture seule). Valeur absente = « non disponible », jamais zéro.

## Argument
- `dirigeant`, `collaboratrice` ou `stagiaire` : déroule uniquement ce parcours.
- Sans argument : demande, en une question, qui est la personne, puis déroule son parcours. Une étape à la fois.
- Pour une page prête à partager avec les trois parcours et des cases à cocher, publie `reference/page-onboarding.html` comme artifact (met à jour les chiffres d'abord).

## Partie commune (toujours)
- Le lieu : 8 passage des Abbesses, Paris 18e, 150 debout / 80 assis ; salle des Je t'aime, salle des Miroirs, accueil des Je t'aime, Jardin d'Éden ; rooftop annoncé, pas ouvert.
- Deux conversions de même poids : demande de devis, visite de l'Atelier. Réponse sous 24 h.
- Jamais : inventer un prix, un chiffre, un témoignage ou une référence client ; choisir entre 240 et 300 m² (à trancher par le dirigeant) ; lancer un seed ou une migration Payload en local (la base locale est celle de production).

## Parcours dirigeant
- Jour 1 : ouvrir `dashboard-ceo.html`, lire la synthèse, valider la liste d'actions de la collaboratrice, vérifier la clé Dolibarr.
- Semaine 1 : trancher la surface (240/300 m²), régime TVA et IS, fin d'exercice, règle acompte/solde et devises, garantie des créances, qui valide les publications, renouveler le jeton `payload-production` (401).
- Mois 1 : point du lundi de 15 minutes, objectif de transformation des devis (départ 9 %), relecture hebdomadaire du calendrier de publications, première clôture avec l'expert-comptable.
- Suivi du lundi : transformation des devis, reste à encaisser et part échue, devis sans réponse > 30 jours, visites programmées, demandes sans réponse après 24 h.

## Parcours collaboratrice
- Jour 1 : accès aux deux instances Dolibarr (extrapp.fr et extrapp.fr/atelier), repérer les 2 comptes bancaires, suivre un devis signé de bout en bout.
- Semaine 1 : rapprocher les paiements, relancer les factures échues (mail, puis appel après 15 jours de retard), commencer par les plus gros montants, relancer les devis ouverts (> 30 jours d'abord), trier les brouillons, noter le motif de chaque refus.
- Mois 1 : relance des devis à J+3 et J+10, rapprochement bancaire hebdomadaire, préparation de la clôture, règle de devise pour les clients hors zone euro.
- Règle : ne jamais supprimer une facture validée ; passer par un avoir et prévenir le dirigeant.

## Parcours stagiaire en communication digitale
- Jour 1 : lire `payload/PRODUCT.md`, parcourir parisprivate.fr sur mobile, accès Postiz (Instagram @parisprivate, Facebook parisprivateevent, LinkedIn), ouvrir `contenus-seminaire/`.
- Semaine 1 : 3 publications issues de l'article séminaire (lumière du lieu, déroulé de journée, check-list), planifiées en brouillon et relues par le dirigeant ; inventaire des photos et vidéos.
- Mois 1 : calendrier sur 4 semaines, un article Payload (français d'abord, règles de `payload/AGENTS.md`), suivi des publications qui déclenchent un devis ou une visite, point mensuel.
- Marque : bleu nuit #00000f, monogramme « P », signature « Concepteur d'évènements sur mesure où l'excellence rencontre l'élégance ». Pas de réglage de marque ou de SEO sans accord du dirigeant. Un client cité dans un post : accord préalable.

## À valider par le dirigeant
Répartition des accès par outil et délais de relance : propositions, pas des règles établies.
