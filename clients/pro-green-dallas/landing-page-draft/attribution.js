/*
 * LOCAL DRAFT - NOT DEPLOYED.
 * Reference click-ID capture and persistence for the canonical Pro Green Dallas landing page.
 * Authoritative spec: clients/pro-green-dallas/canonical-landing-page-developer-handoff.md §6.1
 *
 * Requirements this implements:
 *   - Capture gclid, gbraid, wbraid and all utm_* from the URL
 *   - Persist first-touch values for 90 days (longer than the 60-day click window on the
 *     WhatConverts conversion actions 7717433751 / 7717433754)
 *   - NEVER overwrite a stored click ID with a later empty value
 *   - Record landing URL, referrer, original source and a unique lead_id
 *   - Populate hidden form fields on the page
 *
 * This file embeds no live tag IDs and sends no data anywhere.
 */
(function () {
  'use strict';

  var COOKIE_DOMAIN = '.progreenlandscapesolutions.com';
  var COOKIE_DAYS = 90;
  var PREFIX = 'pg_';

  var CLICK_IDS = ['gclid', 'gbraid', 'wbraid'];
  var UTMS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'utm_id'];
  var TRACKED = CLICK_IDS.concat(UTMS);

  function readCookie(name) {
    var m = document.cookie.match('(^|;)\\s*' + PREFIX + name + '\\s*=\\s*([^;]+)');
    return m ? decodeURIComponent(m[2]) : '';
  }

  function writeCookie(name, value) {
    if (!value) return; // never store an empty value over a real one
    var d = new Date();
    d.setTime(d.getTime() + COOKIE_DAYS * 864e5);
    document.cookie = PREFIX + name + '=' + encodeURIComponent(value) +
      ';expires=' + d.toUTCString() +
      ';path=/;domain=' + COOKIE_DOMAIN + ';SameSite=Lax;Secure';
  }

  function param(name) {
    try {
      return new URLSearchParams(window.location.search).get(name) || '';
    } catch (e) {
      return '';
    }
  }

  /* First-touch wins: keep the stored value unless the URL carries a non-empty new one. */
  function resolve(name) {
    var fromUrl = param(name);
    var stored = readCookie(name);
    if (fromUrl) {
      writeCookie(name, fromUrl);
      return fromUrl;
    }
    return stored;
  }

  function uuid() {
    if (window.crypto && window.crypto.randomUUID) return window.crypto.randomUUID();
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
      var r = (window.crypto && window.crypto.getRandomValues)
        ? window.crypto.getRandomValues(new Uint8Array(1))[0] % 16
        : 0;
      var v = c === 'x' ? r : ((r & 0x3) | 0x8);
      return v.toString(16);
    });
  }

  function originalSource() {
    var stored = readCookie('original_source');
    if (stored) return stored;
    var ref = document.referrer || '';
    var src = param('utm_source');
    var value;
    if (src) value = src;
    else if (CLICK_IDS.some(function (k) { return param(k); })) value = 'google_ads';
    else if (ref) { try { value = new URL(ref).hostname; } catch (e) { value = 'referral'; } }
    else value = 'direct';
    writeCookie('original_source', value);
    return value;
  }

  function landingUrl() {
    var stored = readCookie('landing_url');
    if (stored) return stored;
    writeCookie('landing_url', window.location.href);
    return window.location.href;
  }

  function referrerUrl() {
    var stored = readCookie('referrer_url');
    if (stored) return stored;
    var ref = document.referrer || '';
    if (ref) writeCookie('referrer_url', ref);
    return ref;
  }

  function leadId() {
    var stored = readCookie('lead_id');
    if (stored) return stored;
    var id = uuid();
    writeCookie('lead_id', id);
    return id;
  }

  function consentState() {
    /* Replace with the real consent source at build time. */
    return (window.pgConsent && window.pgConsent.state) || 'unknown';
  }

  function build() {
    var data = {};
    TRACKED.forEach(function (k) { data[k] = resolve(k); });
    data.landing_url = landingUrl();
    data.referrer_url = referrerUrl();
    data.original_source = originalSource();
    data.lead_id = leadId();
    data.consent_state = consentState();
    return data;
  }

  function populate(data) {
    Object.keys(data).forEach(function (key) {
      var fields = document.querySelectorAll('input[type="hidden"][name="' + key + '"]');
      for (var i = 0; i < fields.length; i++) {
        /* Only fill an empty field; never clobber a value already set server-side. */
        if (!fields[i].value) fields[i].value = data[key];
      }
    });
  }

  var attribution = build();
  window.pgAttribution = attribution;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { populate(attribution); });
  } else {
    populate(attribution);
  }

  /* Re-populate if the form is injected late (Gravity Forms AJAX render). */
  if (window.MutationObserver) {
    new MutationObserver(function () { populate(attribution); })
      .observe(document.documentElement, { childList: true, subtree: true });
  }
})();
