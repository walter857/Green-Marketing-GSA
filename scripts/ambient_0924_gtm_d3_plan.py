#!/usr/bin/env python3
"""Ambient | 2026-09-24 | D3 fix plan: stop thank-you PAGEVIEWS counting as form leads.

LOCAL DRAFT ONLY. EXTERNAL WRITES: 0. Writes plans/AMB-0924-GTM-D3.json with a fingerprint.

Verified 2026-09-24 (read-only):
  * GTM-PQTPQ436 trigger "Form - Thank You - Conversions" = Page View AND Page URL contains
    "thank-you". It fires "GA - Form Submission Conversion" (AW-11155434808 /
    GeFgCMmsn9MZELjaqccp = conversion action 6885463625, PRIMARY, no transaction id) and
    "GA - Form Submission Conversion(Microsoft UET)". A direct visit to /thank-you/ fired both.
  * GA4 property 364077190, stream "Ambient Cooling and Heating" G-9X9ZHNCRWF: custom event
    form_submission = event_name equals page_view AND page_location contains thank-you.
    form_submission is a key event and is imported to Google Ads as 7389995485 (secondary).

Method: a per-tab submission token. A tag on every page stores a random token in
sessionStorage when a Gravity Form (form#gform_N) is submitted. The thank-you conversions
fire only when that token exists, carry it as the transaction id (Google Ads dedupes a
repeat), and a cleanup tag deletes it after the page loads. Direct visits, refreshes,
back-button returns and new tabs have no token, so nothing fires. Covers offer gform_1 and
main-site gform_2 alike. No page code and no WordPress change is needed.
"""
from __future__ import annotations
import sys, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import PLANS
from gm_gsa.safety import approval_code

SET_TOKEN_HTML = """<script>
(function () {
  if (window.__gmGfSubmitHooked) return;
  window.__gmGfSubmitHooked = true;
  function isQA(f) {
    try {
      var em = ((f.querySelector('input[type=email]') || {}).value || '').trim().toLowerCase();
      if (em === 'walter@greenmarketingfl.com') return true;
      var txt = [].map.call(f.querySelectorAll('input[type=text], textarea'), function (e) { return e.value; }).join(' ');
      return /test\s*[-–—]\s*do not dispatch/i.test(txt);
    } catch (x) { return false; }
  }
  function newToken(f) {
    return { id: 'gm-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 10),
             t: Date.now(), form: f.id, qa: isQA(f) };
  }
  function errCount() {
    return document.querySelectorAll('.gform_validation_errors, .gfield_error').length;
  }
  // Gravity Forms 2.9 validates in the browser and then submits without a submit event,
  // so the token is set on the submit-button click (Enter also fires this click).
  document.addEventListener('click', function (e) {
    var b = e.target && e.target.closest && e.target.closest('button[type=submit], input[type=submit], .gform_button');
    var f = b && b.closest && b.closest('form');
    if (!f || !f.id || !/^gform_\d+$/.test(f.id)) return;
    var before = errCount(), tok = newToken(f);
    try { sessionStorage.setItem('gm_gf_submit', JSON.stringify(tok)); } catch (x) {}
    // still on the page with MORE errors than before: browser-side validation failed
    setTimeout(function () {
      if (errCount() > before) {
        try {
          var cur = JSON.parse(sessionStorage.getItem('gm_gf_submit') || 'null');
          if (cur && cur.id === tok.id) sessionStorage.removeItem('gm_gf_submit');
        } catch (x) {}
      }
    }, 1500);
  }, true);
  // any native submit path still gets a token
  document.addEventListener('submit', function (e) {
    var f = e.target;
    if (!f || !f.id || !/^gform_\d+$/.test(f.id)) return;
    try { sessionStorage.setItem('gm_gf_submit', JSON.stringify(newToken(f))); } catch (x) {}
  }, true);
  // a failed server-side validation reloads the landing page with errors: drop the token
  function dropOnError() {
    if (errCount() > 0) { try { sessionStorage.removeItem('gm_gf_submit'); } catch (x) {} }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', dropOnError);
  else dropOnError();
})();
</script>"""

TOKEN_VARIABLE_JS = """function () {
  try {
    var v = JSON.parse(sessionStorage.getItem('gm_gf_submit') || 'null');
    if (!v || !v.id || (Date.now() - v.t) > 30 * 60 * 1000) return undefined;
    // Confirmed success only: this page was reached by a fresh navigation that went through
    // the server redirect Gravity Forms sends after a successful POST, referred by a page on
    // this site. Direct visits, refreshes, back/forward and failed attempts all fail this.
    var n = (window.performance && performance.getEntriesByType) ? performance.getEntriesByType('navigation')[0] : null;
    var navType = n ? n.type : ((performance.navigation && performance.navigation.type === 0) ? 'navigate' : 'other');
    var redirects = n ? n.redirectCount : (performance.navigation ? performance.navigation.redirectCount : 0);
    if (navType !== 'navigate' || !(redirects > 0)) return undefined;
    var ref = document.referrer || '';
    if (!ref || ref.indexOf('//' + location.hostname + '/') === -1 || /thank-you/.test(ref)) return undefined;
    // QA submissions never reach Google Ads, Microsoft or GA4 outside GTM Preview
    if (v.qa && !{{Debug Mode}}) return undefined;
    return v.id;
  } catch (x) { return undefined; }
}"""

PHONE_FIX_HTML = """<script>
(function () {
  if (window.__gmPhoneFix) return;
  window.__gmPhoneFix = true;
  // Offer pages are paid destinations: the number shown must be the number dialled,
  // (410) 705-6354. The theme header prints the destination line 410-761-0932, which the
  // all-traffic WhatConverts pool then rewrites to 410-914-1456. Bridge until the markup
  // is fixed; once it is, this tag finds nothing to change.
  var SHOW = '(410) 705-6354';
  var WRONG = /\\(?\\b410\\)?[\\s.\\-]?(?:761[\\s.\\-]?0932|914[\\s.\\-]?1456)\\b/g;
  function fixText(node) {
    if (node && node.nodeValue) {
      WRONG.lastIndex = 0;
      if (WRONG.test(node.nodeValue)) { WRONG.lastIndex = 0; node.nodeValue = node.nodeValue.replace(WRONG, SHOW); }
    }
  }
  function fixTree(root) {
    if (!root) return;
    if (root.nodeType === 3) { fixText(root); return; }
    if (root.nodeType !== 1) return;
    var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false), n;
    while ((n = w.nextNode())) fixText(n);
    var links = root.querySelectorAll('a[href^="tel:"]');
    for (var i = 0; i < links.length; i++) {
      var d = decodeURIComponent(links[i].getAttribute('href')).replace(/\D/g, '').slice(-10);
      if (d === '4107610932' || d === '4109141456') links[i].setAttribute('href', 'tel:+14107056354');
    }
  }
  fixTree(document.body);
  new MutationObserver(function (ms) {
    ms.forEach(function (m) {
      if (m.type === 'characterData') fixText(m.target);
      else for (var i = 0; i < m.addedNodes.length; i++) fixTree(m.addedNodes[i]);
    });
  }).observe(document.body, { subtree: true, childList: true, characterData: true });
})();
</script>"""

CLEAR_TOKEN_HTML = """<script>
try { sessionStorage.removeItem('gm_gf_submit'); } catch (x) {}
</script>"""

PLAN = {
    "customer_id": "2401959466", "exact_account_name": "Ambient Cooling - Live",
    "plan_name": "AMB-0924-GTM-D3", "built_local": "2026-09-24", "version": "v4", "live_version_before": 15, "rollback": "republish version 15",
    "approval_class": "gtm-workspace-build-unpublished + gated ga4-rule-modification",
    "gtm": {"account_id": "6250987248", "container_id": "196198182",
            "public_id": "GTM-PQTPQ436", "container_name": "offer.ambientcoolingandheating.com",
            "workspace": "NEW workspace 'GM D3 thank-you gating 2026-09-24' (default workspace 17 untouched)",
            "versions_created": 0, "publishes": 0},
    "google_ads_api_mutations": 0,
    "objects": [
        {"step": 1, "action": "CREATE", "kind": "Custom HTML tag",
         "name": "GM - GF submit token (set)", "trigger": "All Pages (Page View)",
         "html": SET_TOKEN_HTML, "support_document_write": False},
        {"step": 2, "action": "CREATE", "kind": "Custom JavaScript variable",
         "name": "GM - GF submit token", "code": TOKEN_VARIABLE_JS},
        {"step": 3, "action": "MODIFY", "kind": "Trigger",
         "name": "Form - Thank You - Conversions",
         "from": "Page View; Page URL contains thank-you",
         "to": "Page View; Page URL contains thank-you AND {{GM - GF submit token}} matches RegEx ^gm-"},
        {"step": 4, "action": "MODIFY", "kind": "Google Ads Conversion Tracking tag",
         "name": "GA - Form Submission Conversion",
         "field": "Transaction ID", "from": "(empty)", "to": "{{GM - GF submit token}}",
         "unchanged": ["Conversion ID 11155434808", "Conversion Label GeFgCMmsn9MZELjaqccp",
                       "trigger (now gated by step 3)"]},
        {"step": 5, "action": "NO CHANGE", "kind": "Microsoft UET tag",
         "name": "GA - Form Submission Conversion(Microsoft UET)",
         "note": "shares the trigger, so step 3 gates it too"},
        {"step": 6, "action": "CREATE", "kind": "Trigger",
         "name": "GM - Thank You - Window Loaded",
         "definition": "Window Loaded; Page URL contains thank-you"},
        {"step": 7, "action": "CREATE", "kind": "Custom HTML tag",
         "name": "GM - GF submit token (clear)", "trigger": "GM - Thank You - Window Loaded",
         "html": CLEAR_TOKEN_HTML},
        {"step": 9, "action": "ENABLE", "kind": "Built-in variable", "name": "Debug Mode"},
        {"step": 10, "action": "CREATE", "kind": "Trigger", "name": "GM - Offer pages - DOM Ready",
         "definition": "DOM Ready; Page Hostname equals offer.ambientcoolingandheating.com"},
        {"step": 11, "action": "CREATE", "kind": "Custom HTML tag", "name": "GM - Offer phone consistency",
         "trigger": "GM - Offer pages - DOM Ready", "html": PHONE_FIX_HTML},
        {"step": 8, "action": "MODIFY", "kind": "Google Tag",
         "name": "Google Tag G-9X9ZHNCRWF",
         "field": "Configuration parameter", "add": {"gm_form_submit": "{{GM - GF submit token}}"}},
    ],
    "ga4_after_publish_only": {
        "property": "364077190", "stream": "Ambient Cooling and Heating (G-9X9ZHNCRWF)",
        "custom_event": "form_submission",
        "from": "event_name equals page_view AND page_location contains thank-you",
        "to": "event_name equals page_view AND page_location contains thank-you AND "
              "gm_form_submit starts with gm-",
        "order": "only AFTER the GTM version is published and the parameter is seen in "
                 "DebugView; changing it first would drop every real form_submission"},
    "publication_gate": {
        "requires": "separate explicit approval after Preview QA",
        "preview_qa": [
            "direct visit to /thank-you/: no request with label=GeFgCMmsn9MZELjaqccp, no UET "
            "conversion, page_view has no gm_form_submit",
            "one labelled QA submission on an offer page: exactly one Ads conversion carrying "
            "transaction_id gm-..., one UET conversion, page_view carries gm_form_submit",
            "refresh the thank-you page: nothing fires again",
            "failed submission, browser-side (a required field empty) and server-side: landing page reloads with errors, the token is removed, no conversion fires; the corrected resubmission fires exactly once",
            "main-site gform_2 path cannot be proven until the NitroPack repair; same code"]},
    "effect": "6885463625 stops counting refreshes and direct thank-you visits. Real "
              "submissions keep counting. WhatConverts capture is untouched.",
    "rollback": "publish the previous container version (one click in GTM Versions)",
}
PLAN["operation_count"] = sum(1 for o in PLAN["objects"] if o["action"] != "NO CHANGE")
PLAN["fingerprint"] = approval_code({k: v for k, v in PLAN.items() if k != "fingerprint"})
PLANS.mkdir(parents=True, exist_ok=True)
(PLANS / "AMB-0924-GTM-D3.json").write_text(json.dumps(PLAN, indent=1), encoding="utf-8")
print(f"AMB-0924-GTM-D3: {PLAN['fingerprint']} / {PLAN['operation_count']} GTM objects "
      f"(workspace only, 0 publishes) + 1 GA4 rule edit after publish")
