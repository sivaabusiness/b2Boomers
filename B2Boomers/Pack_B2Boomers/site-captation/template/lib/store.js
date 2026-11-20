// ============================================================
// Persistance des demandes de devis. 2 backends automatiques :
//   1. REST : base Redis Upstash (gratuite) branchée via Vercel
//             → variables KV_REST_API_URL / KV_REST_API_TOKEN
//               (ou UPSTASH_REDIS_REST_URL / _TOKEN)
//   2. FILE : fichier .dev-kv.json en local, pour tester sans base
//
// Modèle : demande:<id> -> JSON · demandes:index -> sorted set par date
//          appel:<id>   -> JSON · appels:index   -> sorted set par date
//          (les clics sur ton numéro, les 500 derniers ; en local :
//           fichier .dev-appels.json)
// ============================================================

import fs from 'node:fs';
import path from 'node:path';

const REST_URL   = process.env.KV_REST_API_URL   || process.env.UPSTASH_REDIS_REST_URL;
const REST_TOKEN = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;
const useRest = !!(REST_URL && REST_TOKEN);

export const backend = useRest ? 'rest' : 'file';

async function rest(cmd) {
  const res = await fetch(REST_URL, {
    method: 'POST',
    headers: { Authorization: `Bearer ${REST_TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(cmd),
  });
  if (!res.ok) throw new Error('KV REST ' + res.status + ' ' + (await res.text()));
  return (await res.json()).result;
}

const FILE = path.join(process.cwd(), '.dev-kv.json');
function readFile() { try { return JSON.parse(fs.readFileSync(FILE, 'utf8')); } catch { return {}; } }
function writeFile(o) { fs.writeFileSync(FILE, JSON.stringify(o, null, 2)); }

export async function saveDemande(d) {
  if (useRest) {
    await rest(['SET', 'demande:' + d.id, JSON.stringify(d)]);
    await rest(['ZADD', 'demandes:index', Date.parse(d.createdAt) || Date.now(), d.id]);
  } else {
    const db = readFile();
    db[d.id] = d;
    writeFile(db);
  }
}

export async function listDemandes() {
  let items;
  if (useRest) {
    const ids = await rest(['ZRANGE', 'demandes:index', 0, -1, 'REV']);
    if (!ids || !ids.length) return [];
    const vals = await rest(['MGET', ...ids.map(id => 'demande:' + id)]);
    items = vals.filter(Boolean).map(v => (typeof v === 'string' ? JSON.parse(v) : v));
  } else {
    items = Object.values(readFile());
  }
  return items.sort((a, b) => new Date(b.createdAt || 0) - new Date(a.createdAt || 0));
}

export async function getDemande(id) {
  if (useRest) {
    const v = await rest(['GET', 'demande:' + id]);
    return v ? (typeof v === 'string' ? JSON.parse(v) : v) : null;
  }
  return readFile()[id] || null;
}

export async function updateDemande(id, patch) {
  const d = await getDemande(id);
  if (!d) return null;
  Object.assign(d, patch);
  if (useRest) {
    await rest(['SET', 'demande:' + id, JSON.stringify(d)]);
  } else {
    const db = readFile();
    db[id] = d;
    writeFile(db);
  }
  return d;
}

export async function deleteDemande(id) {
  if (useRest) {
    await rest(['DEL', 'demande:' + id]);
    await rest(['ZREM', 'demandes:index', id]);
  } else {
    const db = readFile();
    delete db[id];
    writeFile(db);
  }
  return true;
}

// ── Les clics sur ton numéro (api/appel.js) ──
const FILE_APPELS = path.join(process.cwd(), '.dev-appels.json');
const GARDER = 500;
function readAppels() { try { return JSON.parse(fs.readFileSync(FILE_APPELS, 'utf8')); } catch { return []; } }

export async function saveAppel(a) {
  if (useRest) {
    await rest(['SET', 'appel:' + a.id, JSON.stringify(a)]);
    await rest(['ZADD', 'appels:index', Date.parse(a.createdAt) || Date.now(), a.id]);
    const vieux = await rest(['ZRANGE', 'appels:index', 0, -(GARDER + 1)]);
    if (vieux && vieux.length) {
      await rest(['DEL', ...vieux.map(id => 'appel:' + id)]);
      await rest(['ZREMRANGEBYRANK', 'appels:index', 0, -(GARDER + 1)]);
    }
  } else {
    fs.writeFileSync(FILE_APPELS, JSON.stringify([a, ...readAppels()].slice(0, GARDER), null, 2));
  }
}

export async function listAppels(n = 200) {
  if (useRest) {
    const ids = await rest(['ZRANGE', 'appels:index', 0, n - 1, 'REV']);
    if (!ids || !ids.length) return [];
    const vals = await rest(['MGET', ...ids.map(id => 'appel:' + id)]);
    return vals.filter(Boolean).map(v => (typeof v === 'string' ? JSON.parse(v) : v));
  }
  return readAppels().slice(0, n);
}

export async function deleteAppel(id) {
  if (useRest) {
    await rest(['DEL', 'appel:' + id]);
    await rest(['ZREM', 'appels:index', id]);
  } else {
    fs.writeFileSync(FILE_APPELS, JSON.stringify(readAppels().filter(a => a.id !== id), null, 2));
  }
  return true;
}

// Vrai si la clé a déjà été vue dans les `secondes` précédentes (anti-doublon) ; en local : jamais.
export async function dejaVu(cle, secondes) {
  if (!useRest) return false;
  return (await rest(['SET', cle, '1', 'EX', String(secondes), 'NX'])) === null;
}
