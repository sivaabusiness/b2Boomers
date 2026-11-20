// ============================================================
// Écho vers ton espace membre B2Boomers.
// Si la variable B2B_CODE_MEMBRE est posée sur Vercel, chaque
// demande — et chaque changement de statut ou suppression dans
// /demandes — est signalée à ton espace, SANS AUCUNE donnée
// personnelle : ni nom, ni téléphone, ni email, ni adresse, ni
// message. Seulement la date, le service, la commune et la page :
// de quoi compter tes demandes et ton coût par demande.
// Variable absente = rien n'est envoyé. Une panne de l'espace ne
// bloque jamais le formulaire (2,5 s maximum, erreurs avalées).
// ============================================================

const ESPACE = process.env.B2B_URL || 'https://b2boomers-espace.vercel.app';

export async function echoB2B(evenement, d, req) {
  const code = String(process.env.B2B_CODE_MEMBRE || '').trim();
  if (!code || !d) return;
  const ctrl = new AbortController();
  const minuteur = setTimeout(() => ctrl.abort(), 2500);
  try {
    await fetch(ESPACE + '/api/demande', {
      method: 'POST',
      headers: { Authorization: 'Bearer ' + code, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        evenement,
        id: d.id, createdAt: d.createdAt, statut: d.statut,
        service: d.service, commune: d.commune, page: d.page,
        site: String((req && req.headers && (req.headers['x-forwarded-host'] || req.headers.host)) || ''),
      }),
      signal: ctrl.signal,
    });
  } catch (err) {
    console.error('echoB2B', err && err.name === 'AbortError' ? 'timeout' : err);
  } finally {
    clearTimeout(minuteur);
  }
}
