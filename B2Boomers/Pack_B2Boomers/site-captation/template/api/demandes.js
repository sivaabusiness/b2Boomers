// ============================================================
// /api/demandes — le back-office (protégé par mot de passe).
//   GET             → liste des demandes + les clics sur ton numéro
//   PATCH  {id,...} → met à jour statut et/ou note
//   DELETE {id}     → supprime une demande
//   DELETE {appel}  → supprime un clic sur le numéro (tes tests)
// Mot de passe : variable d'environnement ADMIN_PASSWORD,
// envoyé par la page /demandes en en-tête "Authorization: Bearer".
// Statuts et suppressions sont signalés à l'espace membre
// (lib/echo.js) : une demande test supprimée sort des compteurs.
// ============================================================

import { listDemandes, getDemande, updateDemande, deleteDemande, listAppels, deleteAppel } from '../lib/store.js';
import { echoB2B } from '../lib/echo.js';

function authorized(req) {
  const expected = process.env.ADMIN_PASSWORD;
  if (!expected) return false; // pas de mot de passe défini = accès fermé
  const h = String(req.headers.authorization || '');
  return h === 'Bearer ' + expected;
}

export default async function handler(req, res) {
  if (!authorized(req)) {
    return res.status(401).json({ ok: false, error: 'auth' });
  }

  try {
    if (req.method === 'GET') {
      const [demandes, appels] = await Promise.all([listDemandes(), listAppels()]);
      return res.status(200).json({ ok: true, demandes, appels });
    }

    let b = req.body;
    if (typeof b === 'string') { try { b = JSON.parse(b); } catch { b = {}; } }
    b = b || {};
    if (req.method === 'DELETE' && b.appel) {
      await deleteAppel(String(b.appel));
      return res.status(200).json({ ok: true });
    }
    const id = String(b.id || '');
    if (!id) return res.status(422).json({ ok: false, error: 'id' });

    if (req.method === 'PATCH') {
      const patch = {};
      if (typeof b.statut === 'string') patch.statut = b.statut.slice(0, 40);
      if (typeof b.note === 'string') patch.note = b.note.slice(0, 2000);
      const d = await updateDemande(id, patch);
      if (!d) return res.status(404).json({ ok: false, error: 'notfound' });
      if (patch.statut) await echoB2B('statut', d, req);
      return res.status(200).json({ ok: true, demande: d });
    }

    if (req.method === 'DELETE') {
      const d = await getDemande(id);
      await deleteDemande(id);
      await echoB2B('supprimee', d, req);
      return res.status(200).json({ ok: true });
    }

    return res.status(405).json({ ok: false, error: 'method' });
  } catch (err) {
    console.error('api/demandes failed', err);
    return res.status(500).json({ ok: false, error: 'server' });
  }
}
