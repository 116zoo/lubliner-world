# Postiz en local, multi-agence (Paris Private + DCODENFER)

Une seule instance Postiz locale sert les deux marques, parisprivate.fr et dco-denfer.com, chacune dans
sa propre organisation, avec ses réseaux et son calendrier. Ce dossier ne contient que ce mode d'emploi ;
l'installation réelle est ailleurs.

- **Interface** : http://localhost:4007 (inscription / connexion sur `/auth`)
- **Dossier de l'installation** : `/home/ropie/Documents/ChatGPT/JP-Parisprivate/postiz`
  (clone de `gitroomhq/postiz-app`, version 1.47.0 au moment de l'écriture)
- **Fichier Compose** : `docker-compose.yaml` dans ce dossier
- **Outil Compose** : `docker-compose` (v1.29, avec tiret) — le plugin `docker compose` n'est pas installé
- **Image** : `ghcr.io/gitroomhq/postiz-app:latest`, avec Postgres 17, Redis 7.2, Temporal 1.28
  (+ son Postgres et son Elasticsearch), Temporal UI et Spotlight

## Ports utilisés

| Port | Service |
|------|---------|
| 4007 | Postiz (front + API sous `/api`) |
| 7233 | Temporal |
| 8080 | Temporal UI |
| 8969 | Spotlight (débogage) |

## Démarrer / arrêter

Toutes les commandes se lancent depuis le dossier de l'installation :

```bash
cd /home/ropie/Documents/ChatGPT/JP-Parisprivate/postiz
docker-compose up -d        # démarrer
docker-compose ps           # état des conteneurs
docker-compose logs -f postiz   # journaux de l'appli
docker-compose stop         # arrêter (les données sont conservées)
```

Postiz, Postgres et Redis sont en `restart: always` et redémarrent seuls avec le poste. **Temporal, lui, ne
redémarre pas seul** : sans lui, le backend reste bloqué et l'interface ou le MCP renvoient une erreur 502.
Après un redémarrage du poste :

```bash
docker start temporal-postgresql temporal-elasticsearch temporal
sleep 30 && docker exec postiz pm2 restart backend
```

(`temporal-ui` ne démarre pas car le port 8080 est déjà pris sur ce poste ; il n'est pas nécessaire.)
Ne pas utiliser `docker-compose down -v` : le `-v` efface les volumes, donc la base, les comptes et les médias.

## Mettre à jour

```bash
cd /home/ropie/Documents/ChatGPT/JP-Parisprivate/postiz
docker-compose pull postiz
docker-compose up -d postiz
```

Les migrations de base se jouent au démarrage du conteneur. Avant une grosse montée de version, sauvegarder la base :

```bash
docker exec postiz-postgres pg_dump -U postiz-user postiz-db-local > ~/postiz/sauvegarde-$(date +%F).sql
```

## Où sont les secrets et les données

- **Secrets** (JWT_SECRET, mots de passe Postgres, clés d'API des réseaux) : directement dans
  `docker-compose.yaml`, section `environment` du service `postiz`. Il n'y a pas de fichier `.env`.
- **Base de données** : volume Docker `postiz_postgres-volume`
- **Médias envoyés** : volume `postiz_postiz-uploads` (monté sur `/uploads`)
- **Config** : volume `postiz_postiz-config`

⚠️ Le `JWT_SECRET` est encore la valeur par défaut publiée dans le dépôt Postiz. Sans gravité tant que
Postiz n'écoute qu'en local, mais à remplacer avant toute exposition sur Internet
(`openssl rand -hex 32`, puis `docker-compose up -d postiz`). Cela déconnecte les sessions ouvertes.

## Mode multi-agence : une organisation par marque

Dans Postiz, une organisation (Organization) regroupe ses réseaux, ses publications et son équipe.
Un même utilisateur peut appartenir à plusieurs organisations : dès qu'il en a au moins deux, un sélecteur
d'organisation apparaît en haut de l'interface. Il n'y a pas de bouton « nouvelle organisation » :
une organisation se crée **à l'inscription** (champ *Company*), puis on y invite le compte principal.

État au moment de l'écriture : 1 compte, 1 organisation nommée « Extrabase », aucun réseau branché.
Inscription ouverte, pas de facturation (Stripe vide, donc aucune limite), pas de fournisseur d'e-mail
(les invitations passent par un lien à copier).

Marche à suivre (à faire soi-même, une fois par marque) :

1. **Créer l'organisation.** Dans une fenêtre de navigation privée, ouvrir http://localhost:4007/auth et
   s'inscrire avec une autre adresse e-mail (par exemple un alias `+parisprivate` / `+dcodenfer`).
   Mettre le nom de la marque dans *Company* : « Paris Private », puis « DCODENFER ».
2. **Inviter le compte principal.** Toujours dans cette fenêtre : *Settings → Teams → Add member*,
   saisir l'e-mail du compte principal, rôle *Admin*, **décocher l'envoi d'e-mail**, puis copier le lien
   d'invitation (valable 2 jours).
3. **Accepter.** Dans la fenêtre normale, connecté avec le compte principal, coller le lien. L'organisation
   s'ajoute et le sélecteur apparaît en haut.
4. **Facultatif :** renommer « Extrabase » ou la garder pour ce projet.
5. Dans chaque organisation, brancher **ses** réseaux. Un compte Instagram branché dans DCODENFER
   n'apparaît pas dans Paris Private.

## Brancher les réseaux

1. Choisir l'organisation dans le sélecteur, puis *Add channel*.
2. Brancher les réseaux de la marque (Instagram/Facebook, Pinterest, LinkedIn, TikTok…).
   Chaque réseau demande une appli développeur chez le fournisseur et ses identifiants
   (`*_CLIENT_ID` / `*_CLIENT_SECRET`) dans `docker-compose.yaml`, puis `docker-compose up -d postiz`.
   Doc : https://docs.postiz.com/providers
   Une seule appli développeur par réseau suffit pour les deux marques : chaque organisation s'y connecte
   ensuite avec son propre compte de réseau social.

Les publications planifiées ne partent que si le PC est allumé et que les conteneurs tournent.

Limite à connaître : avec `MAIN_URL` sur `localhost`, certains fournisseurs refusent l'URL de retour OAuth
ou ne peuvent pas récupérer les médias. Il faudra peut-être un tunnel HTTPS ou un hébergement public pour ceux-là.

## MCP Postiz dans Claude Code

Postiz expose un serveur MCP (programmer, lister ou supprimer des posts, lister les réseaux, générer des visuels…)
sur `http://localhost:4007/api/mcp`. Chaque **organisation** a sa propre clé d'API : on déclare donc
un serveur MCP par marque, en portée utilisateur (disponible dans tous les projets, rien dans les dépôts).

```bash
~/postiz/brancher-mcp.sh               # liste les organisations
~/postiz/brancher-mcp.sh "DCODENFER"   # ajoute (ou remplace) le serveur postiz-dcodenfer
claude mcp list | grep postiz          # vérifie : ✔ Connected
```

Le script lit la clé dans la base locale sans l'afficher. Elle est enregistrée dans `~/.claude.json`, en
en-tête `Authorization: Bearer …`. Relancer le script après une régénération de clé
(*Settings → Public API*) ou après la création d'une nouvelle organisation.
Les serveurs ajoutés ne sont visibles que dans les **nouvelles** sessions Claude Code.

Branchés à ce jour : `postiz-extrabase`, `postiz-zarius42`.

Le mode OAuth de Postiz (`/api/mcp-oauth-claude`) ne fonctionne pas sur cette installation. Ses adresses de
découverte perdent le préfixe `/api` et retombent sur la page de connexion, d'où l'usage de la clé d'API.
