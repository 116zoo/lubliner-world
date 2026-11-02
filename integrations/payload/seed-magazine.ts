/**
 * Crée la catégorie « Magazine blog » et l'article central dans le Payload de
 * Paris Private, en BROUILLON (rien n'est publié).
 *
 * Lancement, depuis le dossier du projet Payload (celui qui contient payload.config.ts) :
 *   ./node_modules/.bin/payload run /chemin/vers/integrations/payload/seed-magazine.ts
 *
 * Variables : ARTICLE_MD (défaut : l'article de ce dépôt), IMAGE (défaut : la photo du dépôt).
 * Idempotent : un second lancement met à jour l'article existant (même slug) au lieu d'en créer un autre.
 * ⚠ Cible la base décrite par POSTGRES_URL du projet Payload : vérifiez-la avant de lancer.
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import config from '@payload-config'
import { getPayload } from 'payload'

const here = path.dirname(fileURLToPath(import.meta.url))
const root = path.resolve(here, '../..')
const articlePath =
  process.env.ARTICLE_MD ||
  path.join(root, 'content/magazine/salle-polyvalente-paris-seminaire-anniversaire-camp-de-base.md')

const parseFront = (raw: string) => {
  const m = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/)
  if (!m) throw new Error('Front matter manquant')
  const meta: Record<string, string> = {}
  for (const line of m[1].split('\n')) {
    const i = line.indexOf(':')
    if (i > 0) meta[line.slice(0, i).trim()] = line.slice(i + 1).trim().replace(/^"|"$/g, '')
  }
  return { meta, body: m[2] }
}

const text = (t: string, format = 0) => ({ type: 'text', text: t, format, detail: 0, mode: 'normal', style: '', version: 1 })
const block = (type: string, children: unknown[], extra = {}) => ({
  type, children, direction: 'ltr', format: '', indent: 0, version: 1, ...extra,
})

/** Texte inline : [libellé](url) devient un lien, **gras** un texte gras. */
const inline = (s: string): unknown[] => {
  const out: unknown[] = []
  const re = /\[([^\]]+)\]\(([^)]+)\)|\*\*([^*]+)\*\*/g
  let last = 0
  for (const m of s.matchAll(re)) {
    if (m.index! > last) out.push(text(s.slice(last, m.index)))
    if (m[1]) {
      out.push(block('link', [text(m[1])], { fields: { url: m[2], linkType: 'custom', newTab: true } }))
    } else out.push(text(m[3], 1))
    last = m.index! + m[0].length
  }
  if (last < s.length) out.push(text(s.slice(last)))
  return out
}

const toLexical = (md: string) => {
  const children: unknown[] = []
  let list: { ordered: boolean; items: unknown[] } | null = null
  const flush = () => {
    if (!list) return
    children.push(
      block('list', list.items, { listType: list.ordered ? 'number' : 'bullet', start: 1, tag: list.ordered ? 'ol' : 'ul' }),
    )
    list = null
  }
  for (const line of md.split('\n')) {
    const l = line.trimEnd()
    const li = l.match(/^(?:(\d+)\.|-)\s+(.*)$/)
    if (li) {
      const ordered = Boolean(li[1])
      if (!list || list.ordered !== ordered) { flush(); list = { ordered, items: [] } }
      list.items.push(block('listitem', inline(li[2]), { value: list.items.length + 1 }))
      continue
    }
    flush()
    const h = l.match(/^(#{2,3})\s+(.*)$/)
    if (h) children.push(block('heading', inline(h[2]), { tag: `h${h[1].length}` }))
    else if (l.trim()) children.push(block('paragraph', inline(l), { textFormat: 0 }))
  }
  flush()
  return { root: block('root', children) }
}

/** Questions/réponses de la section FAQ → answerBlocks (AEO). */
const faq = (md: string) => {
  const part = md.split(/^## FAQ\s*$/m)[1] || ''
  return [...part.matchAll(/^### (.+)\n\n([\s\S]*?)(?=\n### |\s*$)/gm)].map((m) => ({
    question: m[1].trim(),
    answer: m[2].replace(/\s+/g, ' ').trim(),
  }))
}

const payload = await getPayload({ config })
const { meta, body } = parseFront(fs.readFileSync(articlePath, 'utf8'))

// 1. Catégorie
const cats = await payload.find({ collection: 'categories', where: { slug: { equals: meta.category } }, limit: 1, locale: 'fr' })
const category =
  cats.docs[0] ??
  (await payload.create({ collection: 'categories', locale: 'fr', data: { title: 'Magazine blog', slug: meta.category } as never }))

// 2. Image (informative, avec texte alternatif)
const imagePath = process.env.IMAGE || path.resolve(path.dirname(articlePath), meta.image)
const existingMedia = await payload.find({ collection: 'media', where: { filename: { equals: path.basename(imagePath) } }, limit: 1 })
const media =
  existingMedia.docs[0] ??
  (await payload.create({
    collection: 'media',
    locale: 'fr',
    data: { role: 'informative', alt: meta.image_alt } as never,
    file: { data: fs.readFileSync(imagePath), mimetype: 'image/webp', name: path.basename(imagePath), size: fs.statSync(imagePath).size },
  }))

// 3. Article (brouillon, idempotent sur le slug)
const content = toLexical(body.replace(/^## FAQ[\s\S]*$/m, '').trim())
const data = {
  title: meta.title,
  slug: meta.slug,
  heroImage: media.id,
  content,
  categories: [category.id],
  meta: { title: meta.meta_title, description: meta.meta_description, image: media.id },
  aeo: { aeoSummary: meta.meta_description, answerBlocks: faq(body) },
  _status: 'draft' as const,
}
const found = await payload.find({ collection: 'posts', where: { slug: { equals: meta.slug } }, limit: 1, draft: true, locale: 'fr' })
const post = found.docs[0]
  ? await payload.update({ collection: 'posts', id: found.docs[0].id, data: data as never, draft: true, locale: 'fr' })
  : await payload.create({ collection: 'posts', data: data as never, draft: true, locale: 'fr' })

console.log(`Brouillon prêt : posts/${post.id} (catégorie ${category.id}, média ${media.id})`)
process.exit(0)
