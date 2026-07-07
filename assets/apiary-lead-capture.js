(() => {
  const WEBHOOK_URL = 'https://n8n.esq2u.com/webhook/apiary-foundry/lead';
  const BOOKING_URL = 'https://tidycal.com/peacockesq/apiary-foundry-1-1-chats';
  const ATTR_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'gclid', 'gbraid', 'wbraid', 'fbclid', 'msclkid'];
  const STORAGE_KEY = 'apiary_attribution_v1';

  const nowIso = () => new Date().toISOString();
  const currentUrl = () => window.location.href;

  function readStoredAttribution() {
    try { return JSON.parse(window.localStorage.getItem(STORAGE_KEY) || '{}') || {}; }
    catch (_) { return {}; }
  }

  function writeStoredAttribution(data) {
    try { window.localStorage.setItem(STORAGE_KEY, JSON.stringify(data)); }
    catch (_) { /* storage may be blocked; lead capture still works */ }
  }

  function captureAttribution() {
    const params = new URLSearchParams(window.location.search);
    const stored = readStoredAttribution();
    const next = { ...stored };

    ATTR_KEYS.forEach((key) => {
      const value = params.get(key);
      if (value) {
        next[key] = value;
        next[`${key}_captured_at`] = nowIso();
      }
    });

    if (!next.first_landing_page_url) {
      next.first_landing_page_url = currentUrl();
      next.first_referrer_url = document.referrer || '';
      next.first_seen_at = nowIso();
    }

    next.last_page_url = currentUrl();
    next.last_referrer_url = document.referrer || next.last_referrer_url || '';
    next.last_seen_at = nowIso();
    writeStoredAttribution(next);
    return next;
  }

  function getOrCreateId(key, prefix) {
    const stored = readStoredAttribution();
    if (stored[key]) return stored[key];
    const id = `${prefix}-${Math.random().toString(36).slice(2)}-${Date.now().toString(36)}`;
    stored[key] = id;
    writeStoredAttribution(stored);
    return id;
  }

  function bookingUrlFor(email) {
    const url = new URL(BOOKING_URL);
    const cleanEmail = String(email || '').trim();
    const attribution = readStoredAttribution();
    if (cleanEmail) url.searchParams.set('email', cleanEmail);
    ATTR_KEYS.forEach((key) => {
      const value = attribution[key];
      if (value) url.searchParams.set(key, value);
    });
    if (attribution.first_landing_page_url) url.searchParams.set('landing_page_url', attribution.first_landing_page_url);
    if (attribution.first_referrer_url) url.searchParams.set('referrer_url', attribution.first_referrer_url);
    return url.toString();
  }

  function refreshBookingLinks(email) {
    document.querySelectorAll('[data-booking-link]').forEach((link) => {
      link.setAttribute('href', bookingUrlFor(email || link.dataset.email || ''));
    });
  }

  function formToPayload(form) {
    const data = new FormData(form);
    const attribution = captureAttribution();
    const payload = {
      event_id: `apiary-${Date.now()}-${Math.random().toString(36).slice(2)}`,
      event_time: nowIso(),
      event_name: form.dataset.eventName || 'lead_created',
      source_system: 'apiary_foundry_site',
      source_business: 'apiary_foundry',
      source_site: 'apiaryfoundry.com',
      source_form: form.dataset.sourceForm || form.getAttribute('id') || 'lead_form',
      anonymous_id: getOrCreateId('anonymous_id', 'anon'),
      session_id: window.sessionStorage.getItem('apiary_session_id') || (() => {
        const id = `sess-${Math.random().toString(36).slice(2)}-${Date.now().toString(36)}`;
        try { window.sessionStorage.setItem('apiary_session_id', id); } catch (_) {}
        return id;
      })(),
      name: String(data.get('name') || '').trim(),
      email: String(data.get('email') || '').trim(),
      phone: String(data.get('phone') || '').trim(),
      company: String(data.get('company') || '').trim() || 'Apiary Foundry',
      message: String(data.get('message') || '').trim(),
      page_url: currentUrl(),
      landing_page_url: attribution.first_landing_page_url || currentUrl(),
      referrer_url: attribution.first_referrer_url || document.referrer || '',
      consent_status: data.get('marketing_consent') ? 'granted' : 'not_granted',
      consent_region: Intl.DateTimeFormat().resolvedOptions().timeZone || '',
      consent_text: form.querySelector('[data-consent-text]')?.textContent?.trim() || '',
      properties: {
        form_location: form.dataset.formLocation || '',
        current_path: window.location.pathname,
        user_agent: navigator.userAgent,
        message: String(data.get('message') || '').trim(),
        marketing_consent: Boolean(data.get('marketing_consent')),
        newsletter_consent: Boolean(data.get('marketing_consent'))
      }
    };

    ATTR_KEYS.forEach((key) => { payload[key] = attribution[key] || ''; });
    return payload;
  }

  function setStatus(form, message, state, html) {
    const status = form.querySelector('[data-form-status]');
    if (!status) return;
    if (html) status.innerHTML = message;
    else status.textContent = message;
    status.dataset.state = state || '';
  }

  async function submitLeadForm(form) {
    const payload = formToPayload(form);
    if (!payload.email) {
      setStatus(form, 'Email is required. No mystery meat.', 'error');
      return;
    }
    if (form.querySelector('[name="marketing_consent"]') && !payload.properties.marketing_consent) {
      setStatus(form, 'Please check the consent box so Apiary Foundry can follow up.', 'error');
      return;
    }

    const submit = form.querySelector('[type="submit"]');
    if (submit) submit.disabled = true;
    setStatus(form, 'Sending...', 'pending');

    try {
      const res = await fetch(WEBHOOK_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const link = bookingUrlFor(payload.email);
      refreshBookingLinks(payload.email);
      setStatus(
        form,
        `Received. You are on the list. If you want the free 30-minute audit call too, <a href="${link}" data-booking-link>book it here</a>.`,
        'success',
        true
      );
      form.reset();
    } catch (error) {
      setStatus(form, 'Submission failed. Email team@williepeacock.com and mention Apiary Foundry.', 'error');
      console.error('Apiary lead capture failed', error);
    } finally {
      if (submit) submit.disabled = false;
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    captureAttribution();
    refreshBookingLinks('');
    document.querySelectorAll('[name="email"]').forEach((input) => {
      input.addEventListener('input', () => refreshBookingLinks(input.value));
    });
    document.querySelectorAll('form[data-apiary-lead-form]').forEach((form) => {
      form.addEventListener('submit', (event) => {
        event.preventDefault();
        submitLeadForm(form);
      });
    });
  });
})();
