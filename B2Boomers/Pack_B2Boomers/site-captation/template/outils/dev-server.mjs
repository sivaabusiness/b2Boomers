// ============================================================
// Serveur de test local (optionnel — le déploiement Vercel n'en
// a pas besoin). Lance :  node outils/dev-server.mjs
// puis ouvre http://localhost:3456
// Les demandes de test s'écrivent dans .dev-kv.json.
// ============================================================

import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const PORT = Number(process.env.PORT) || 3456;
process.env.ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'test';

const MIME = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.webp': 'image/webp', '.ico': 'image/x-icon' };

function nodeRes(res) {
  return {
    _code: 200,
    // en local, jamais de cache : chaque modification se voit tout de suite
    setHeader(k, v) { res.setHeader(k, /^cache-control$/i.test(k) ? 'no-store' : v); return this; },
    status(c) { this._code = c; return this; },
    json(o) { res.writeHead(this._code, { 'Content-Type': 'application/json' }); res.end(JSON.stringify(o)); return this; },
    end(s) { res.writeHead(this._code); res.end(s); return this; },
  };
}

http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://localhost');
  let p = decodeURIComponent(url.pathname);

  // API : /api/<nom> → api/<nom>.js
  if (p.startsWith('/api/')) {
    const mod = path.join(ROOT, 'api', p.slice(5).replace(/[^a-z0-9\-]/gi, '') + '.js');
    if (!fs.existsSync(mod)) { res.writeHead(404); return res.end('api introuvable'); }
    let body = '';
    for await (const chunk of req) body += chunk;
    const { default: handler } = await import('file://' + mod + '?t=' + Date.now());
    const fakeReq = { method: req.method, headers: req.headers, body };
    try { await handler(fakeReq, nodeRes(res)); }
    catch (e) { console.error(e); res.writeHead(500); res.end('erreur handler'); }
    return;
  }

  // Statique : / → index.html, /demandes → demandes.html
  if (p === '/') p = '/index.html';
  if (!path.extname(p)) p += '.html';
  const file = path.join(ROOT, p);
  if (!file.startsWith(ROOT) || !fs.existsSync(file)) { res.writeHead(404); return res.end('introuvable'); }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(file)] || 'application/octet-stream' });
  res.end(fs.readFileSync(file));
}).listen(PORT, () => {
  console.log('Site de test : http://localhost:' + PORT);
  console.log('Back-office  : http://localhost:' + PORT + '/demandes  (mot de passe : ' + process.env.ADMIN_PASSWORD + ')');
});
