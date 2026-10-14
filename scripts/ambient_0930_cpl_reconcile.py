#!/usr/bin/env python3
"""Ambient | 2026-09-30 | READ-ONLY CPL reconciliation under the client CPL policy (target $280, ceiling $350).

CPL = all ad spend in scope and window (every click type) / UNIQUE GENUINE PAID leads attributable to it.
Paid proof, per lead:  (a) session click id (gclid) that resolves in this account's click_view, or
                        (b) a WhatConverts call matched to a Google call_view record (start +-150 s, duration +-5 s).
Genuine: not QA (dropped by fetch_leads), not spam, not Quotable=No, calls >= 60 s or Quotable=Yes.
Unique: one per contact (sha256 of normalised phone/email, never printed) inside the window; later touches
from the same contact are reported, not counted.
Attribution date = click date (click_view) or call date (call_view); spend uses the same dates, so the
windows are consistent. Leads that arrived after the window end are shown as lag. 2026-09-30 is PARTIAL.
No PII, no call content and no staff names are printed or written.
"""
from __future__ import annotations
import sys, json, re, hashlib, datetime, collections
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, TZ, SNAP, CLIENT_DIR, ROOT  # noqa: E402
from gm_gsa.config import load_dotenv_if_available  # noqa: E402
from gm_gsa.whatconverts import fetch_leads  # noqa: E402

START = "2026-08-14"   # first delivery of the current Search build; history is never reset
_T = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.datetime.now(ZoneInfo("America/New_York")).date()
TODAY, LAST = _T.isoformat(), (_T - datetime.timedelta(days=1)).isoformat()
_L7, _L14 = (_T - datetime.timedelta(days=7)).isoformat(), (_T - datetime.timedelta(days=14)).isoformat()
HEAT = ["24257819463", "24257819466", "24132507744", "24268690038", "24268690041", "24279798229", "24274160783"]
COOL = ["24132507741", "24132507750", "24132507753", "24132507747"]
WINDOWS = {"launch_to_date": (START, LAST), "cooling_uncapped": (START, "2026-09-03"), "cooling_capped": ("2026-09-04", "2026-09-21"),
           "sept_mtd": ("2026-09-01", LAST), "heating_build_to_date": ("2026-09-17", LAST), "since_migration": ("2026-09-24", LAST),
           "last7": (_L7, LAST), "last14": (_L14, LAST), "today_provisional": (TODAY, TODAY)}
OUT = SNAP / f"cpl-reconciliation-{TODAY}.json"  # v2 rules (2026-09-30c)
UTC = ZoneInfo("UTC")
REASONS = {"wrong_number": r"wrong number|misdial|dialed the wrong|not the right (company|number)",
           "solicitation": r"solicit|vendor|marketing agency|advertis|seo|sales rep|partnership",
           "job_seeker": r"job|employment|hiring|resume|apply for",
           "no_conversation": r"no one (spoke|answered)|silence|no conversation|disconnected",
           "existing_customer_admin": r"invoice|payment|billing|reschedul",
           "out_of_area": r"out of (the )?(service )?area|outside (the|our) (service )?area",
           "service_not_offered": r"don'?t (offer|provide)|not a service"}
EXCLUDING = {"wrong_number", "solicitation", "job_seeker", "no_conversation"}
OPPORTUNITY_DAYS = 14   # same contact inside 14 days = same opportunity


def days(a, b):
    d, e = datetime.date.fromisoformat(a), datetime.date.fromisoformat(b)
    while d <= e:
        yield d.isoformat(); d += datetime.timedelta(days=1)


c = client()
ident = identity_gate(c, verbose=True)

# ---------------- spend (all click types), daily, campaign + ad group ----------------
camp_name, ag_name, ag_camp = {}, {}, {}
spend_c = collections.defaultdict(float); spend_g = collections.defaultdict(float)
clicks_c = collections.Counter(); clicks_g = collections.Counter()
for r in q(c, f"""SELECT campaign.id, campaign.name, segments.date, metrics.cost_micros, metrics.clicks FROM campaign
        WHERE segments.date BETWEEN '{START}' AND '{TODAY}' AND metrics.impressions > 0"""):
    k = (str(r.campaign.id), r.segments.date); camp_name[k[0]] = r.campaign.name
    spend_c[k] += r.metrics.cost_micros / 1e6; clicks_c[k] += r.metrics.clicks
for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group.name, segments.date, metrics.cost_micros, metrics.clicks FROM ad_group
        WHERE segments.date BETWEEN '{START}' AND '{TODAY}' AND metrics.impressions > 0"""):
    g = str(r.ad_group.id); ag_name[g] = r.ad_group.name; ag_camp[g] = str(r.campaign.id)
    spend_g[(g, r.segments.date)] += r.metrics.cost_micros / 1e6; clicks_g[(g, r.segments.date)] += r.metrics.clicks
for r in q(c, "SELECT campaign.id, campaign.name, campaign.status FROM campaign WHERE campaign.status != 'REMOVED'"):
    camp_name.setdefault(str(r.campaign.id), r.campaign.name)

# ---------------- click_view: gclid -> campaign / ad group / click date ----------------
gmap = {}
for d in days(START, TODAY):
    for r in q(c, f"""SELECT click_view.gclid, campaign.id, ad_group.id, segments.click_type, segments.date
            FROM click_view WHERE segments.date = '{d}'"""):
        gmap[r.click_view.gclid] = dict(campaign=str(r.campaign.id), ad_group=str(r.ad_group.id), date=d,
                                        click_type=E(r.segments.click_type))
print(f"click_view gclids {START}..{TODAY}: {len(gmap)}")

# ---------------- call_view ----------------
calls = []
for r in q(c, f"""SELECT call_view.start_call_date_time, call_view.call_duration_seconds, call_view.call_status,
        call_view.type, campaign.id, ad_group.id FROM call_view WHERE call_view.start_call_date_time >= '{START} 00:00:00'"""):
    calls.append(dict(start=r.call_view.start_call_date_time, dur=r.call_view.call_duration_seconds, status=E(r.call_view.call_status),
                      type=E(r.call_view.type), campaign=str(r.campaign.id), ad_group=str(r.ad_group.id)))
print(f"call_view records since {START}: {len(calls)}")

# ---------------- Google credited conversions (primary) by click date and by conversion date ----------------
g_conv_click = collections.defaultdict(float); g_conv_cd = collections.defaultdict(float)
for r in q(c, f"""SELECT campaign.id, ad_group.id, segments.date, segments.conversion_action_name, metrics.conversions
        FROM ad_group WHERE segments.date BETWEEN '{START}' AND '{TODAY}' AND metrics.conversions > 0"""):
    g_conv_click[(str(r.ad_group.id), r.segments.date, r.segments.conversion_action_name)] += r.metrics.conversions
for r in q(c, f"""SELECT campaign.id, segments.date, segments.conversion_action_name, metrics.conversions_by_conversion_date
        FROM campaign WHERE segments.date BETWEEN '{START}' AND '{TODAY}' AND metrics.conversions_by_conversion_date > 0"""):
    g_conv_cd[(str(r.campaign.id), r.segments.date, r.segments.conversion_action_name)] += r.metrics.conversions_by_conversion_date

# ---------------- WhatConverts: default + duplicate + spam ----------------
load_dotenv_if_available(ROOT / ".env")
cy = CLIENT_DIR / "client.yaml"
leads, seen = [], set()
for label, flt in (("default", {}), ("duplicate", {"duplicate": "true"}), ("spam", {"spam": "true"})):
    for l in fetch_leads("115814", "105803", START, TODAY, client_yaml=cy, **flt)["leads"]:
        if l["lead_id"] in seen:
            continue
        seen.add(l["lead_id"]); l["_set"] = label; leads.append(l)


def contact_key(l):
    ph = re.sub(r"\D", "", str(l.get("contact_phone_number") or l.get("caller_number") or l.get("phone_number") or ""))[-10:]
    em = str(l.get("contact_email_address") or "").strip().lower()
    raw = ph or em or f"lead:{l['lead_id']}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def et(ts):
    return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(TZ)


rows = []
for l in leads:
    t = et(l["date_created"])
    la = l.get("lead_analysis") if isinstance(l.get("lead_analysis"), dict) else {}
    row = dict(lead_id=l["lead_id"], set=l["_set"], lead_et=t.strftime("%Y-%m-%d %H:%M"), date=t.date().isoformat(),
               type=l.get("lead_type"), source=f"{l.get('lead_source')}/{l.get('lead_medium')}",
               number=str(l.get("tracking_number") or "")[-4:], dur=l.get("call_duration_seconds"),
               quotable=l.get("quotable") or "Not Set", status=l.get("lead_status"), spam=bool(l.get("spam")) or l["_set"] == "spam",
               call_type=la.get("Call Type"), customer_type=la.get("Customer Type"), disposition=la.get("Call Disposition"),
               landing=re.sub(r"\?.*$", "", l.get("landing_url") or "").replace("https://", ""),
               has_gclid=bool(l.get("gclid")), has_braid=bool(l.get("gbraid") or l.get("wbraid")), contact=contact_key(l))
    m = gmap.get(l.get("gclid") or "")
    if m:
        row.update(paid="CLICK_ID", campaign=m["campaign"], ad_group=m["ad_group"], attr_date=m["date"], click_type=m["click_type"])
    elif row["type"] == "Phone Call":
        best = None
        for cv in calls:
            ct = datetime.datetime.fromisoformat(cv["start"]).replace(tzinfo=TZ)
            dt = abs((ct - t).total_seconds())
            if dt <= 150 and (row["dur"] is None or abs((cv["dur"] or 0) - (row["dur"] or 0)) <= 5):
                if not best or dt < best[0]:
                    best = (dt, cv)
        if best:
            cv = best[1]; cv["_matched"] = l["lead_id"]
            row.update(paid="CALL_VIEW", campaign=cv["campaign"], ad_group=cv["ad_group"], attr_date=cv["start"][:10], click_type="CALL")
    if "paid" not in row:
        row["paid"] = "GCLID_NOT_IN_ACCOUNT" if row["has_gclid"] else ("BRAID_ONLY" if row["has_braid"] else "NONE")
    # genuineness (v2, 2026-09-30c): Quotable=No is NOT an exclusion by itself; the reason is reviewed from WhatConverts'
    # own analysis text / call transcript / form field values (scanned on disk, never printed).
    text = " ".join(str(v) for k, v in la.items() if k in ("Lead Summary", "Topic Detection", "Intent Detection", "Keyword Detection"))
    text += " " + str(l.get("call_transcription") or "")
    af = l.get("additional_fields")
    if isinstance(af, dict):
        text += " " + " ".join(str(v) for v in af.values())
    signals = [k for k, rx in REASONS.items() if re.search(rx, text, re.I)]
    reasons = []
    if row["spam"]: reasons.append("spam")
    reasons += [k for k in signals if k in EXCLUDING]
    if row["disposition"] == "Ringing Hangup": reasons.append("hangup")
    row["reason_signals"] = signals
    row["has_review_text"] = bool(text.strip())
    if reasons:
        row["verification"] = "EXCLUDED"
    elif row["type"] == "Phone Call" and (row["dur"] or 0) < 60 and row["quotable"] != "Yes" and not row["has_review_text"]:
        row["verification"] = "UNVERIFIED"          # short call, nothing to review: sensitivity only
    else:
        row["verification"] = "VERIFIED"
    row["genuine"] = row["verification"] == "VERIFIED"; row["exclusion"] = reasons
    row["qualified"] = row["quotable"] == "Yes"
    rows.append(row)

# uniqueness per window: first genuine lead per contact inside the window
first_contact_date = {}
for r in sorted(rows, key=lambda x: x["lead_et"]):
    first_contact_date.setdefault(r["contact"], r["lead_et"])


def counted(win, include_unverified=False):
    """Unique paid OPPORTUNITIES: same contact within OPPORTUNITY_DAYS = one opportunity (not one per contact forever)."""
    a, b = WINDOWS[win]
    out, last_seen = [], {}
    ok = {"VERIFIED", "UNVERIFIED"} if include_unverified else {"VERIFIED"}
    for r in sorted(rows, key=lambda x: x["lead_et"]):
        if r["paid"] not in ("CLICK_ID", "CALL_VIEW") or r["verification"] not in ok:
            continue
        if not (a <= r["attr_date"] <= b):
            continue
        d = datetime.date.fromisoformat(r["date"])
        prev = last_seen.get(r["contact"])
        last_seen[r["contact"]] = d
        if prev and (d - prev).days <= OPPORTUNITY_DAYS:
            r.setdefault("merged_into_earlier_opportunity", True); continue
        out.append(r)
    return out


def google_only_calls(win):
    """Google call records (paid by definition) with no WhatConverts record: genuineness unknown, sensitivity only."""
    a, b = WINDOWS[win]
    return [cv for cv in calls if "_matched" not in cv and a <= cv["start"][:10] <= b]


def spend(ids, win, level="c"):
    a, b = WINDOWS[win]
    src = spend_c if level == "c" else spend_g
    return round(sum(v for (i, d), v in src.items() if i in ids and a <= d <= b), 2)


def clicks(ids, win, level="c"):
    a, b = WINDOWS[win]
    src = clicks_c if level == "c" else clicks_g
    return sum(v for (i, d), v in src.items() if i in ids and a <= d <= b)


def band(sp, n):
    if n == 0:
        return "ZERO_LEAD_STOP" if sp >= 300 else ("ZERO_LEAD_ALERT" if sp >= 280 else "ZERO_LEAD_WATCH" if sp > 0 else "NO_SPEND")
    cpl = sp / n
    return "MET" if cpl <= 280 else ("FREEZE" if cpl <= 350 else "BREACH")


res = {"identity": {k: ident[k] for k in ("customer_id", "descriptive_name")}, "windows": WINDOWS, "scopes": {}, "leads": rows,
       "unmatched_call_views": [cv for cv in calls if "_matched" not in cv], "google_conv_click": {}, "google_conv_convdate": {}}
scopes = {"ACCOUNT (all Search)": ("c", set(camp_name)), "HEATING PROGRAM (7 campaigns)": ("c", set(HEAT)),
          "COOLING (4 campaigns)": ("c", set(COOL))}
for cid in HEAT + COOL:
    scopes[f"C {cid} {camp_name.get(cid, '')[18:60]}"] = ("c", {cid})
for g, cid in ag_camp.items():
    if cid in HEAT:
        scopes[f"G {g} {ag_name[g][7:]}"] = ("g", {g})
for win in WINDOWS:
    lw, lu, gc = counted(win), counted(win, include_unverified=True), google_only_calls(win)
    inside = lambda r, lvl, ids: (r["campaign"] in ids if lvl == "c" else r["ad_group"] in ids)
    for name, (lvl, ids) in scopes.items():
        sp = spend(ids, win, lvl)
        n = sum(1 for r in lw if inside(r, lvl, ids))
        nq = sum(1 for r in lw if inside(r, lvl, ids) and r["qualified"])
        ns = sum(1 for r in lu if inside(r, lvl, ids)) + sum(1 for cv in gc if (cv["campaign"] in ids if lvl == "c" else cv["ad_group"] in ids))
        if sp == 0 and n == 0 and ns == 0:
            continue
        res["scopes"].setdefault(name, {})[win] = dict(
            spend=sp, clicks=clicks(ids, win, lvl), leads=n, qualified=nq, sensitivity_leads=ns,
            cpl=round(sp / n, 2) if n else None, cpql=round(sp / nq, 2) if nq else None,
            sensitivity_cpl=round(sp / ns, 2) if ns else None,
            band=band(sp, n) if win != "today_provisional" else "PROVISIONAL")
# Google credited primary conversions per campaign/window (click date) for duplication comparison
for win in ("sept_mtd", "since_migration", "launch_to_date"):
    a, b = WINDOWS[win]
    tot = collections.Counter()
    for (g, d, act), v in g_conv_click.items():
        if a <= d <= b:
            tot[ag_camp.get(g, "?")] += v
    res["google_conv_click"][win] = {k: round(v, 2) for k, v in tot.items()}
res["google_conv_convdate"] = {f"{k[0]}|{k[1]}|{k[2]}": round(v, 2) for k, v in g_conv_cd.items() if k[1] >= "2026-09-01"}
# ---- v2: call-path classification, organic GBP calls, Google WC Lead credits beyond click-ID leads (enhanced conversions) ----
CALL_ASSET_NUMS, PAID_LOC_NUMS, GBP_NUMS = {"6354", "9517"}, {"4650"}, {"4021", "7280", "9803"}
for r in rows:
    if r["paid"] == "CALL_VIEW":
        r["call_path"] = "call_asset" if r["number"] in CALL_ASSET_NUMS else "paid_location_asset" if r["number"] in PAID_LOC_NUMS | GBP_NUMS else "other"
    elif r["type"] == "Phone Call" and r["number"] in GBP_NUMS:
        r["call_path"] = "organic_business_profile"
ct_day = collections.defaultdict(collections.Counter)
for cv in res["unmatched_call_views"]:
    for x in q(c, f"""SELECT ad_group.id, segments.click_type, metrics.clicks, metrics.impressions FROM ad_group
            WHERE ad_group.id = {cv['ad_group']} AND segments.date = '{cv['start'][:10]}'"""):
        if x.metrics.clicks or x.metrics.impressions:
            ct_day[f"{cv['ad_group']}|{cv['start'][:10]}"][E(x.segments.click_type)] += x.metrics.clicks
    k = ct_day[f"{cv['ad_group']}|{cv['start'][:10]}"]
    cv["likely_path"] = "call_asset_or_call_button" if k.get("CALLS") else "location_asset (no call-button clicks that day)"
    cv["click_types_that_day"] = dict(k)
ec = []
wc_credit = collections.defaultdict(float)
for (g, d, act), v in g_conv_click.items():
    if act == "WC Lead":
        wc_credit[(ag_camp.get(g, "?"), d)] += v
clickid_by = collections.Counter((r["campaign"], r["attr_date"]) for r in rows if r["paid"] == "CLICK_ID")
for (cid, d), v in sorted(wc_credit.items()):
    extra = round(v - clickid_by.get((cid, d), 0), 2)
    if extra > 0:
        ec.append(dict(campaign=cid, click_date=d, wc_lead_credited=v, click_id_leads=clickid_by.get((cid, d), 0), credited_without_click_id=extra))
res["wc_lead_credits_without_click_id"] = ec
res["call_paths"] = collections.Counter(r.get("call_path") for r in rows if r.get("call_path"))
OUT.write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")

# ---------------- print ----------------
print("\n=== PAID-CANDIDATE LEADS (click id / call_view / google-cpc label), no PII ===")
for r in sorted(rows, key=lambda x: x["lead_et"]):
    if r["paid"] in ("CLICK_ID", "CALL_VIEW") or r["source"].endswith("/cpc") or r["has_gclid"]:
        print(f"  {r['lead_id']} {r['lead_et']} {r['type'][:10]:10s} set={r['set']:9s} {r['source'][:22]:22s} #{r['number']:4s} dur={r['dur']} "
              f"q={r['quotable']:7s} st={r['status']} cust={r['customer_type']} ctype={r['call_type']} paid={r['paid']:20s} "
              f"camp={r.get('campaign','-')} ag={ag_name.get(r.get('ag','') or r.get('ad_group',''), '-')[7:30]} attr={r.get('attr_date','-')} "
              f"{r['verification']} {r['exclusion'] or ''} q={r['quotable']} path={r.get('call_path','-')} land={r['landing'][:30]}")
print("\n=== call_view records with no WhatConverts match ===")
for cv in res["unmatched_call_views"]:
    print("  ", cv["start"], cv["dur"], cv["status"], camp_name.get(cv["campaign"], cv["campaign"])[18:50], ag_name.get(cv["ad_group"], cv["ad_group"])[7:], "|", cv.get("likely_path"), cv.get("click_types_that_day"))
print("\n=== label-only google/cpc leads (no click id, no call match) by window ===")
for win in ("sept_mtd", "since_migration"):
    a, b = WINDOWS[win]
    lab = [r for r in rows if r["paid"] == "NONE" and r["source"].endswith("/cpc") and a <= r["date"] <= b]
    print(f"  {win}: {len(lab)} -> {[(r['lead_id'], r['type'][:5], r['number'], r['quotable'], r['exclusion']) for r in lab]}")
print("\n=== LAG: counted leads that arrived after their window end ===")
for win in ("sept_mtd", "since_migration"):
    lw = counted(win)
    print(f"  {win}: {[(r['lead_id'], r['attr_date'], r['date']) for r in lw if r['date'] > WINDOWS[win][1]]}")
print("\n=== SCOPES: spend | clicks | unique genuine paid leads | CPL | band ===")
for name, ws in res["scopes"].items():
    line = []
    for win in ("launch_to_date", "sept_mtd", "heating_build_to_date", "since_migration", "last7", "today_provisional"):
        v = ws.get(win)
        if v:
            line.append(f"{win}: ${v['spend']:.2f}/{v['clicks']}c/{v['leads']}L/{'$%.0f' % v['cpl'] if v['cpl'] else 'undef'}/{v['band']}")
    print(f"  {name[:48]:48s} " + " | ".join(line))
print("\n=== Google credited primary conversions (click date) by campaign ===")
for win, v in res["google_conv_click"].items():
    print(f"  {win}: " + ", ".join(f"{camp_name.get(k, k)[18:45]}={x}" for k, x in v.items()))
print("\nwrote", OUT)
