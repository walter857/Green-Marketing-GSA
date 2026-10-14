TASK TITLE:

[P0] Softwind Power Washing — Correct Google tag scope and duplicate GTM load

TASK DESCRIPTION:

**Problem 1 — Google Tag Manager is installed twice**

GTM-P3LD97NN is bootstrapped twice in the delivered HTML of every page:

| Artifact | Count |
|---|---|
| Inline bootstrap (window,document,'script','dataLayer','GTM-P3LD97NN') | 2 |
| script src=".../gtm.js?id=GTM-P3LD97NN" tags | 2 |
| noscript ns.html?id=GTM-P3LD97NN iframes | 2 |
| GTM-P3LD97NN string occurrences | 6 |
| dataLayer after load | gtm.js, **gtm.js**, gtm.dom, gtm.load |

Two container instances initialise, so every tag in the container can fire twice — including
Google Ads conversions. The browser de-duplicates the network fetch to one gtm.js, which is why
a network-only check misses this. The dataLayer proves both bootstraps ran.

The two inline bootstraps differ in whitespace, which indicates two different injectors — most
likely a theme or header setting plus a plugin such as Site Kit, a GTM plugin, or a custom-code
block.

**Required result**

- GTM-P3LD97NN is installed exactly once, intentionally, from one known place
- No second bootstrap and no second noscript iframe
- dataLayer shows exactly one gtm.js entry
- Existing consent behaviour remains intact
- **Please report which two sources you found** — we need to know which one to keep

**Problem 2 — identify the source of both Google Ads tags (investigation only)**

Two Google Ads tags load as async gtag.js script tags on every page:

```
https://www.googletagmanager.com/gtag/js?id=AW-18369652705&cx=c&gtm=4e68v1   <- correct account
https://www.googletagmanager.com/gtag/js?id=AW-17878095007&cx=c&gtm=4e68v1   <- sibling account
```

Each ID appears exactly once in the rendered source and only inside that injected script URL —
there is no literal gtag('config','AW-17878095007', ...) anywhere in the page HTML.

Please confirm, naming the file or setting, whether:

1. Both are configured inside GTM container GTM-P3LD97NN
2. One or both are hardcoded in the theme, child theme, functions.php, an mu-plugin or a tag
   plugin
3. One or both come from a Google Site Kit or Google Ads plugin
4. Something else

**Critical scope limits**

- **Preserve AW-18369652705.** That is the correct Softwind Power Washing account.
- **Do NOT remove AW-17878095007 globally.** It belongs to Softwind Landscape & Masonry
  (Google Ads customer 2429758629) and may legitimately be required on that brand's own pages.
  Scoping it away from the Power Washing URLs requires a separate approval from that account's
  owner, which Green Marketing is arranging. Under this task we only need the source
  identified — no tag removed or modified.

**Acceptance criteria**

- [ ] Exactly one inline bootstrap, one gtm.js tag, one noscript iframe
- [ ] dataLayer contains one gtm.js entry
- [ ] All existing tags still fire exactly once
- [ ] Consent behaviour unchanged
- [ ] Injection source named for AW-18369652705 and AW-17878095007
- [ ] No tag removed or modified

**Rollback:** restore the removed bootstrap snippet.
