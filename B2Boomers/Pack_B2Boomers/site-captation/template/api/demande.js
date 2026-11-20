// ============================================================
// POST /api/demande — reçoit le formulaire de devis du site.
// Valide, stocke la demande, et (si configuré) notifie sur
// Telegram et prévient l'espace membre B2Boomers (sans données
// personnelles). C'est le seul endpoint public du moteur.
// ============================================================

import { saveDemande } from '../lib/store.js';
import { echoB2B } from '../lib/echo.js';

function cleanTel(tel) {
  return String(tel || '').replace(/[\s.\-()]/g, '');
}
function isValidPhone(tel) {
  const c = cleanTel(tel);
  if (/^\+[1-9]\d{7,14}$/.test(c)) return true; // international
  return /^0[1-9]\d{8}$/.test(c);               // format FR local
}
// Un e-mail plausible ou rien : la case est libre côté visiteur, on ne garde jamais autre chose
// qu'une adresse (pas de guillemets, chevrons ni espaces : rien qui puisse devenir du code).
function emailPropre(v) {
  const s = String(v || '').trim().slice(0, 120);
  return /^[^\s@"'<>()\,;:]+@[^\s@"'<>()\,;:]+\.[a-z]{2,}$/i.test(s) ? s : '';
}
// Texte libre du formulaire, coupé à une longueur raisonnable.
function txt(v, max) {
  return String(v || '').trim().slice(0, max);
}

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
  if (req.method !== 'POST') {
    return res.status(405).json({ ok: false, error: 'method' });
  }

  let b = req.body;
  if (typeof b === 'string') b = Object.fromEntries(new URLSearchParams(b));
  b = b || {};

  // Honeypot anti-bot : un humain ne remplit jamais ce champ caché.
  if (b.site_web && String(b.site_web).trim() !== '') {
    return res.status(400).json({ ok: false, error: 'spam' });
  }

  const nom = txt(b.nom, 100);
  if (!nom) return res.status(422).json({ ok: false, error: 'nom' });
  if (!isValidPhone(b.tel)) return res.status(422).json({ ok: false, error: 'tel' });
  const service = txt(b.service, 80);
  if (!service) return res.status(422).json({ ok: false, error: 'service' });

  const demande = {
    id: Date.now().toString(36) + Math.random().toString(36).slice(2, 8),
    createdAt: new Date().toISOString(),
    statut: 'nouvelle',
    nom,
    tel: cleanTel(b.tel),
    email: emailPropre(b.email),
    commune: txt(b.commune, 100),
    adresse: txt(b.adresse, 200),
    service,
    description: txt(b.description, 2000),
    page: txt(b.page, 300),
    note: '',
  };

  // On stocke AVANT de notifier : une demande ne doit jamais se perdre.
  try {
    await saveDemande(demande);
  } catch (err) {
    console.error('saveDemande failed', err);
    return res.status(500).json({ ok: false, error: 'store' });
  }

  // Notification Telegram — optionnelle (variables d'env absentes = ignorée).
  try {
    await notifyTelegram(demande, domaine(req));
  } catch (err) {
    console.error('notifyTelegram failed', err);
  }

  // Écho espace membre — optionnel (B2B_CODE_MEMBRE absent = ignoré).
  await echoB2B('nouvelle', demande, req);

  return res.status(200).json({ ok: true, id: demande.id });
}

async function notifyTelegram(d, site) {
  const token = process.env.TELEGRAM_TOKEN;
  const chat = process.env.TELEGRAM_CHAT_ID;
  if (!token || !chat) return; // pas configuré : pas de notif, pas d'erreur

  const wa = d.tel.startsWith('+') ? d.tel.slice(1) : ('33' + d.tel.replace(/^0/, ''));
  const text =
    `📥 <b>Nouvelle demande — ${esc(d.service)}</b>\n` +
    (site ? `🌐 ${esc(site)}\n` : '') +
    (d.commune ? `📍 ${esc(d.commune)}${d.adresse ? ' · ' + esc(d.adresse) : ''}\n` : '') +
    `👤 <b>${esc(d.nom)}</b>\n` +
    `📱 <b>${esc(d.tel)}</b> · <a href="https://wa.me/${wa}">WhatsApp</a>\n` +
    (d.email ? `✉️ ${esc(d.email)}\n` : '') +
    (d.description ? `\n💬 ${esc(d.description)}` : '');

  const res = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: chat,
      text,
      parse_mode: 'HTML',
      disable_web_page_preview: true,
    }),
  });
  if (!res.ok) throw new Error('Telegram ' + res.status + ' ' + (await res.text()));
}
