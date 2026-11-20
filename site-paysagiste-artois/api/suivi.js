// ============================================================
// /api/suivi — tout le suivi du site, en une ligne dans le <head> :
//   <script src="/api/suivi" defer></script>
//
//   1. Les clics sur ton numéro (liens tel:) → /api/appel : notif sur
//      TON Telegram avec l'heure exacte + liste dans /demandes, pour
//      vérifier les appels avec l'artisan. Sans cookie, rien ne part
//      vers l'espace B2Boomers.
//   2. Les conversions Google Ads : formulaire envoyé, clic sur le
//      numéro, appels depuis le site (numéro de transfert Google).
//   3. Les formulaires (data-moteur) : devis en 2 temps, rappel express,
//      message « pensez à décrocher » — les pages n'ont aucun script.
// Aucun outil de mesure d'audience (Microsoft Clarity retiré le 07/11 :
// son bandeau de cookies coûtait des demandes). Sans GADS_ID, le site ne
// dépose aucun cookie et n'affiche AUCUN bandeau. Avec GADS_ID, Google Ads
// ne dépose rien avant « Accepter » sur une fine barre en bas (choix
// gardé 6 mois, « Refuser » aussi simple).
//
// Réglages (variables Vercel) — absentes = la partie concernée ne se
// charge pas, sans erreur :
//   GADS_ID           identifiant Google Ads des conversions (AW-123456789)
//   GADS_FORMULAIRE   libellé de la conversion « formulaire »
//   GADS_CLIC_TEL     libellé de la conversion « clic sur le numéro »
//   GADS_APPEL_SITE   libellé de la conversion « appels depuis le site »
//   GADS_NUMERO       ton numéro, écrit EXACTEMENT comme sur le site
//                     (Google le remplace par un numéro de transfert
//                     pour les visiteurs venus de la pub)
//   SANS_BANDEAU = 1  pour se passer de la barre d'accord — à tes risques :
//                     la CNIL demande l'accord du visiteur.
// ============================================================

function propre(v, re, max) {
  return String(v || '').trim().replace(re, '').slice(0, max);
}

export function reglages(env) {
  return {
    gads: /^AW-\d{6,15}$/.test(String(env.GADS_ID || '').trim()) ? String(env.GADS_ID).trim() : '',
    formulaire: propre(env.GADS_FORMULAIRE, /[^\w-]/g, 40),
    clicTel: propre(env.GADS_CLIC_TEL, /[^\w-]/g, 40),
    appelSite: propre(env.GADS_APPEL_SITE, /[^\w-]/g, 40),
    numero: propre(env.GADS_NUMERO, /[^\d +.()-]/g, 25),
    bandeau: env.SANS_BANDEAU !== '1',
  };
}

export function script(cfg) {
  return `(function(){
  if (window.__suiviSite) return; window.__suiviSite = true;
  var CFG = ${JSON.stringify(cfg)};
  var CLE = 'suivi-accord', SIX_MOIS = 182 * 864e5;

  // D'où vient la visite (gardé le temps de la visite) : la pub Google laisse un gclid dans l'adresse.
  var src = 'direct';
  try {
    if (/[?&](gclid|gbraid|wbraid)=/.test(location.search)) src = 'Google Ads';
    else if (/google\\./.test(document.referrer)) src = 'Google';
    else if (document.referrer && document.referrer.indexOf(location.host) === -1) src = 'autre site';
    var vu = sessionStorage.getItem('suivi-src');
    if (vu && src !== 'Google Ads') src = vu; else sessionStorage.setItem('suivi-src', src);
  } catch (e) {}

  // Google Ads, en mode consentement : rien n'est stocké avant « Accepter ».
  window.dataLayer = window.dataLayer || [];
  function gtag(){ window.dataLayer.push(arguments); }
  if (CFG.gads) {
    gtag('consent', 'default', { ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied', analytics_storage: 'denied' });
    var g = document.createElement('script'); g.async = true; g.src = 'https://www.googletagmanager.com/gtag/js?id=' + CFG.gads;
    document.head.appendChild(g);
    gtag('js', new Date());
    gtag('config', CFG.gads);
    if (CFG.appelSite && CFG.numero) gtag('config', CFG.gads + '/' + CFG.appelSite, { phone_conversion_number: CFG.numero });
  }
  function conversion(libelle){ if (CFG.gads && libelle) gtag('event', 'conversion', { send_to: CFG.gads + '/' + libelle }); }

  // 1. Clic sur le numéro : notre suivi (sans cookie) + la conversion Google Ads.
  document.addEventListener('click', function(e){
    var a = e.target && e.target.closest && e.target.closest('a[href^="tel:"]');
    if (!a) return;
    var data = JSON.stringify({ page: location.pathname, numero: a.getAttribute('href').slice(4),
      appareil: /Mobi|Android|iPhone|iPad/i.test(navigator.userAgent) ? 'mobile' : 'ordinateur', source: src });
    var parti = false;
    try { parti = !!(navigator.sendBeacon && navigator.sendBeacon('/api/appel', new Blob([data], { type: 'application/json' }))); } catch (x) {}
    if (!parti) try { fetch('/api/appel', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: data, keepalive: true }); } catch (y) {}
    conversion(CFG.clicTel);
  }, true);

  // 2. Formulaire envoyé : le script du formulaire passe par fetch('/api/demande') ; une réponse OK = une conversion.
  if (CFG.gads && CFG.formulaire && window.fetch) {
    var f0 = window.fetch;
    window.fetch = function(u, o){
      var p = f0.apply(this, arguments);
      try {
        if (String((u && u.url) || u).indexOf('/api/demande') !== -1 && o && String(o.method || '').toUpperCase() === 'POST')
          p.then(function(r){ if (r && r.ok) conversion(CFG.formulaire); }, function(){});
      } catch (e) {}
      return p;
    };
  }

  // 3. Les formulaires du moteur — les pages n'ont aucun script de formulaire :
  //    <form data-moteur="devis"> en 2 temps, celui des pages tunnel (la question en gros boutons,
  //    puis les coordonnées ; data-service="…" sur la balise = directement les coordonnées) et
  //    <form data-moteur="rappel"> (prénom + téléphone). Envoi vers /api/demande, puis le message
  //    « pensez à décrocher » avec « Appelez maintenant ». Les anciens formulaires (sans
  //    data-moteur) gardent leur propre script.
  // Le numéro du « Appelez maintenant » : data-tel du formulaire (les pages tunnel n'affichent aucun
  // numéro, pour qu'on n'en sorte pas avant d'avoir envoyé), sinon le 1er lien tel: de la page.
  function merci(f){
    var d = f && f.getAttribute('data-tel'), t = document.querySelector('a[href^="tel:"]');
    var lien = d ? 'tel:' + d.replace(/[^+0-9]/g, '') : (t ? t.getAttribute('href') : '');
    return '<div class="form-ok" role="status"><b>✅ C’est bien envoyé, merci !</b><br><br>On vous rappelle aujourd’hui, ' +
      'au plus tard sous 24 h, au numéro indiqué. <b>Pensez à décrocher</b>, même si le numéro ne vous dit rien : c’est sûrement pour votre devis.' +
      (lien ? '<br><br>Vraiment pressé ? <a href="' + lien + '">📞 Appelez maintenant</a>' : '') + '</div>';
  }
  function moteur(f){
    if (f.__moteur) return; f.__moteur = true;
    var el = f.elements, rappel = f.getAttribute('data-moteur') === 'rappel', fixe = f.getAttribute('data-service');
    var e1 = f.querySelector('[data-etape="1"]'), e2 = f.querySelector('[data-etape="2"]');
    // au changement d'étape, si le haut du formulaire est sorti de l'écran, on le fait revenir
    function voir(){ var h = f.getBoundingClientRect().top; if (h < 10) scrollBy({ top: h - 16, behavior: 'smooth' }); }
    function coordonnees(service, libelle){
      if (el.service) el.service.value = service;
      var c = f.querySelector('[data-choisi]'); if (c) c.textContent = libelle || service;
      if (e1) e1.hidden = true;
      if (e2) e2.hidden = false;
    }
    if (fixe && !rappel) coordonnees(fixe);
    f.querySelectorAll('button[data-service]').forEach(function(b){
      b.addEventListener('click', function(){ coordonnees(b.getAttribute('data-service'), b.textContent.trim()); voir(); });
    });
    var r = f.querySelector('[data-retour]');
    if (r) r.addEventListener('click', function(){ if (e1 && e2) { e1.hidden = false; e2.hidden = true; voir(); } });
    f.addEventListener('submit', function(ev){
      ev.preventDefault();
      var val = function(n){ return el[n] ? String(el[n].value || '').trim() : ''; };
      if (val('site_web')) return;
      var service = rappel ? (fixe || 'Travaux') + ' — rappel demandé' : val('service');
      if (!val('nom') || !val('tel') || (!rappel && (!val('commune') || !service))) {
        alert(rappel ? 'Il manque votre prénom ou votre téléphone.'
          : 'Il manque une information : votre nom, votre téléphone et votre commune suffisent.');
        return;
      }
      var btn = f.querySelector('button[type=submit]'), texte = btn ? btn.textContent : '';
      if (btn) { btn.disabled = true; btn.textContent = 'Envoi en cours…'; }
      fetch('/api/demande', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ nom: val('nom'), tel: val('tel'), email: '', commune: val('commune'), adresse: '',
          service: service, page: location.pathname, site_web: '',
          description: val('description') || (rappel ? '(rappel demandé — pas de détail)' : '(pas de détail — à voir par téléphone)') }) })
        .then(function(res){ return res.json(); })
        .then(function(j){ if (!j || !j.ok) throw new Error((j && j.error) || 'envoi'); f.outerHTML = merci(f); })
        .catch(function(e){
          if (btn) { btn.disabled = false; btn.textContent = texte; }
          alert(e && e.message === 'tel' ? 'Le numéro de téléphone ne semble pas complet : vérifiez-le.'
            : 'L’envoi n’a pas fonctionné. Merci de réessayer dans un instant.');
        });
    });
  }
  document.querySelectorAll('form[data-moteur]').forEach(moteur);
  // L'annonce arrive sur l'accueil avec ?travaux=<service> : le titre prend le nom du service
  // ([data-titre-travaux]) et son gros bouton ([data-travaux="<service>"]) est mis en avant.
  try {
    var tr = new URLSearchParams(location.search).get('travaux');
    var tuile = tr && document.querySelector('[data-travaux="' + tr.replace(/[^\\w-]/g, '') + '"]');
    if (tuile) {
      document.querySelectorAll('[data-titre-travaux]').forEach(function(e){ e.textContent = tuile.getAttribute('data-nom') || e.textContent; });
      tuile.classList.add('choisie');
      var ph = tuile.querySelector('img'), fond = document.querySelector('[data-photo-travaux]');
      if (ph && fond) fond.style.backgroundImage = 'url("' + ph.getAttribute('src') + '")';
      if (tuile.parentNode) tuile.parentNode.insertBefore(tuile, tuile.parentNode.firstChild);
    }
  } catch (e) {}
  // La barre collante du bas (data-barre) : cachée tant que le formulaire du haut est à l'écran
  // (les gros boutons du devis y sont déjà), elle revient dès qu'on descend.
  //    Le bloc qui la cache : [data-cacher-barre] (les gros boutons du haut de l'accueil), sinon #devis.
  var barre = document.querySelector('[data-barre]'), prevu = false;
  function cache(){ return document.querySelector('[data-cacher-barre]') || document.getElementById('devis'); }
  function majBarre(){
    prevu = false;
    var f = cache(), r = f && f.getBoundingClientRect();
    barre.style.transform = r && r.top < innerHeight - 80 && r.bottom > 120 ? 'translateY(130%)' : '';
  }
  function planifier(){ if (!prevu) { prevu = true; setTimeout(majBarre, 60); } }
  if (barre && cache()) {
    barre.style.transition = 'transform .25s ease';
    addEventListener('scroll', planifier, { passive: true });
    addEventListener('resize', planifier);
    addEventListener('load', planifier);
    planifier();
  }

  // 4. L'accord du visiteur — seulement si les conversions Google Ads sont branchées.
  function accord(){
    gtag('consent', 'update', { ad_storage: 'granted', ad_user_data: 'granted', analytics_storage: 'granted' });
  }
  if (!CFG.gads) return;                          // rien qui demande l'accord du visiteur : aucun bandeau
  if (!CFG.bandeau) { accord(); return; }
  var choix = null;
  try { choix = JSON.parse(localStorage.getItem(CLE) || 'null'); } catch (e) {}
  if (choix && Date.now() - choix.t < SIX_MOIS) { if (choix.v === 'oui') accord(); return; }
  function garder(v){ try { localStorage.setItem(CLE, JSON.stringify({ v: v, t: Date.now() })); } catch (e) {} }
  // Une fine barre en bas, sur une ligne (deux sur téléphone) : discrète, sans voile sur la page.
  function bandeau(){
    var b = document.createElement('div');
    b.setAttribute('role', 'region');
    b.setAttribute('aria-label', 'Cookies');
    var mobile = innerWidth < 760;
    b.style.cssText = 'position:fixed;left:50%;transform:translateX(-50%);bottom:' + (mobile ? 86 : 14) + 'px;z-index:2147483000;' +
      'width:calc(100% - 20px);max-width:560px;display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px;' +
      'background:rgba(255,255,255,.97);color:#1d1d1b;border:1px solid #dcd8cc;border-radius:10px;padding:7px 8px 7px 12px;' +
      'box-shadow:0 4px 16px rgba(0,0,0,.12);font:12.5px/1.35 system-ui,-apple-system,Segoe UI,sans-serif';
    var bt = 'padding:6px 12px;border-radius:7px;border:1px solid #c9c5b9;background:#fff;color:inherit;font:inherit;font-weight:600;cursor:pointer';
    b.innerHTML = '<span style="flex:1;min-width:180px">Cookies de mesure de nos annonces Google. ' +
      '<a href="/confidentialite.html" style="color:inherit">En savoir plus</a></span>' +
      '<span style="display:flex;gap:6px"><button type="button" data-c="non" style="' + bt + '">Refuser</button>' +
      '<button type="button" data-c="oui" style="' + bt + '">Accepter</button></span>';
    b.addEventListener('click', function(e){
      var v = e.target && e.target.getAttribute && e.target.getAttribute('data-c');
      if (!v) return;
      garder(v);
      b.remove();
      if (v === 'oui') accord();
    });
    document.body.appendChild(b);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', bandeau); else bandeau();
})();`;
}

export default function handler(req, res) {
  res.setHeader('Content-Type', 'application/javascript; charset=utf-8');
  res.setHeader('Cache-Control', 'public, max-age=600');
  return res.status(200).end(script(reglages(process.env)));
}
