// ============================================================
// POST /api/appel — un visiteur a appuyé sur ton numéro de téléphone
// (envoyé par /api/suivi). Sans cookie ni donnée personnelle : la
// page, le type d'appareil, la source de la visite, l'heure.
// Le clic est gardé pour ton back-office (/demandes → « Clics sur ton
// numéro ») et sonne sur TON Telegram (le même bot que les demandes) :
// tu sais à quelle heure vérifier avec l'artisan qu'il a eu l'appel.
// Rien ne part vers l'espace B2Boomers.
// Anti-doublon : un même visiteur ne compte qu'une fois toutes les 20 secondes
// (double appui).
// ============================================================

import crypto from 'node:crypto';
import { saveAppel, dejaVu } from '../lib/store.js';

function esc(s) {
  return String(s == null ? '' : s).replace(/[&<>"]/g, c => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]
  ));
}

// Le site d'où vient la requête (elagage-belfort.fr) : avec plusieurs sites sur le même
// Telegram, la notif dit de quel site elle vient.
function domaine(req) {
  return String((req && req.headers && (req.headers['x-forwarded-host'] || req.headers.host)) || '')
    .split(',')[0].trim().replace(/:\d+$/, '').replace(/^www\./i, '').slice(0, 80);
}

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'method' });

  let b = req.body;
  if (typeof b === 'string') { try { b = JSON.parse(b); } catch { b = Object.fromEntries(new URLSearchParams(b)); } }
  b = b || {};

  // le visiteur, sans garder son adresse IP : une empreinte qui ne sert qu'à l'anti-doublon
  const ip = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim();
  const empreinte = crypto.createHash('sha256').update(ip + '|' + (req.headers['user-agent'] || '')).digest('hex').slice(0, 16);
  if (ip && await dejaVu('appel-vu:' + empreinte, 20)) return res.status(200).json({ ok: true, doublon: true });

  const appel = {
    id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
    createdAt: new Date().toISOString(),
    page: String(b.page || '').slice(0, 200),
    numero: String(b.numero || '').replace(/[^\d+]/g, '').slice(0, 20),
    appareil: b.appareil === 'mobile' ? 'mobile' : 'ordinateur',
    source: String(b.source || '').slice(0, 30),
  };
  try {
    await saveAppel(appel);
  } catch (err) {
    console.error('saveAppel failed', err);
    return res.status(500).json({ ok: false, error: 'store' });
  }
  try {
    await notifyTelegram(appel, domaine(req));
  } catch (err) {
    console.error('notifyTelegram (appel) failed', err);
  }
  return res.status(200).json({ ok: true });
}

async function notifyTelegram(a, site) {
  const token = process.env.TELEGRAM_TOKEN;
  const chat = process.env.TELEGRAM_CHAT_ID;
  if (!token || !chat) return; // pas configuré : pas de notif, pas d'erreur
  const d = new Date(a.createdAt);
  const jour = d.toLocaleDateString('fr-FR', { timeZone: 'Europe/Paris', weekday: 'long', day: 'numeric', month: 'long' });
  const heure = d.toLocaleTimeString('fr-FR', { timeZone: 'Europe/Paris', hour: '2-digit', minute: '2-digit' }).replace(':', ' h ');
  const text =
    `📞 <b>Clic sur ton numéro — ${heure}</b>\n` +
    (site ? `🌐 ${esc(site)}\n` : '') +
    `🗓 ${esc(jour)}\n` +
    `📄 ${esc(a.page || '/')} · ${a.appareil === 'mobile' ? '📱 mobile' : '💻 ordinateur'}` +
    (a.source ? ` · ${esc(a.source)}` : '') + '\n' +
    `→ Note l'heure : au débrief, demande à l'artisan s'il a eu un appel vers ${heure}.`;
  const res = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: chat, text, parse_mode: 'HTML', disable_web_page_preview: true }),
  });
  if (!res.ok) throw new Error('Telegram ' + res.status + ' ' + (await res.text()));
}
