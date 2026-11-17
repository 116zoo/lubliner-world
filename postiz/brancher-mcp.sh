#!/usr/bin/env bash
# Branche le MCP Postiz d'une organisation dans Claude Code (portée utilisateur).
# La clé d'API est lue dans la base locale et n'est jamais affichée.
#   ./brancher-mcp.sh                 -> liste les organisations
#   ./brancher-mcp.sh "DCODENFER"     -> ajoute le serveur MCP postiz-dcodenfer
set -euo pipefail

psql() { docker exec -i postiz-postgres psql -U postiz-user -d postiz-db-local -tA "$@"; }

if [ $# -eq 0 ]; then
  echo "Organisations disponibles :"
  psql -c 'select name from "Organization" order by "createdAt";' | sed 's/^/  - /'
  exit 0
fi

org="$1"
key=$(psql -v org="$org" <<'SQL'
select "apiKey" from "Organization" where name = :'org' limit 1;
SQL
)
if [ -z "$key" ]; then
  echo "Organisation « $org » introuvable ou sans clé d'API." >&2
  echo "Organisations existantes :" >&2
  psql -c 'select name from "Organization" order by "createdAt";' | sed 's/^/  - /' >&2
  echo "Pour en créer une : s'inscrire sur http://localhost:4007/auth avec « $org » dans le champ Company." >&2
  exit 1
fi

slug=$(printf '%s' "$org" | iconv -f utf-8 -t ascii//TRANSLIT | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-*//;s/-*$//')
name="postiz-$slug"

claude mcp remove -s user "$name" >/dev/null 2>&1 || true
claude mcp add -s user --transport http "$name" http://localhost:4007/api/mcp \
  --header "Authorization: Bearer $key" >/dev/null
echo "Serveur MCP « $name » ajouté (organisation « $org »)."
