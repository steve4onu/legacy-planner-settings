#!/usr/bin/env python3
"""Fetch live NGX share/ETF prices and CBN exchange rates and write prices.json.

Run by the GitHub Action in this repository. The Legacy Portfolio Planner web app
reads prices.json (GitHub serves it with CORS enabled, which the exchange's own
API does not). Links come from planner-settings.json so they can be changed
without touching this script. If a source fails, the previous values are kept.
"""
import json, os, sys, urllib.request, urllib.parse, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULTS = {
    'ngx_equities_url': 'https://doclib.ngxgroup.com/REST/api/statistics/equities/?market=&sector=&orderby=&pageSize=300&pageNo=0',
    'ngx_ticker_url': 'https://doclib.ngxgroup.com/REST/api/statistics/ticker',
    'fx_url': 'https://www.cbn.gov.ng/api/GetAllExchangeRates',
}
UA = {'User-Agent': 'Mozilla/5.0 (LegacyPortfolioPlanner price job)', 'Accept': 'application/json'}

def get_json(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8-sig'))

def as_list(j):
    if isinstance(j, list): return j
    if isinstance(j, dict):
        for k in ('data', 'Data', 'value'):
            if isinstance(j.get(k), list): return j[k]
    return []

def field(r, name):
    if name in r: return r[name]
    for k in r:
        if k.lower() == name.lower(): return r[k]
    return None

def num(x):
    try:
        v = float(str(x).replace(',', ''))
        return v if v == v else None
    except Exception:
        return None

def iso(x):
    if not x: return None
    s = str(x).strip()
    if s.startswith('/Date('):
        ms = int(s[6:].split(')')[0].split('+')[0].split('-')[0] or 0)
        return datetime.datetime.utcfromtimestamp(ms / 1000).strftime('%Y-%m-%d')
    if len(s) >= 10 and s[4] == '-' and s[7] == '-': return s[:10]
    for fmt in ('%d/%m/%Y', '%m/%d/%Y %I:%M:%S %p', '%d/%m/%Y %H:%M:%S'):
        try: return datetime.datetime.strptime(s[:len(fmt) + 4].strip(), fmt).strftime('%Y-%m-%d')
        except Exception: pass
    return None

def main():
    settings = {}
    try: settings = json.load(open(os.path.join(ROOT, 'planner-settings.json'), encoding='utf-8'))
    except Exception as e: print('settings not read:', e)
    S = lambda k: settings.get(k) or DEFAULTS[k]
    out_path = os.path.join(ROOT, 'prices.json')
    try: prev = json.load(open(out_path, encoding='utf-8'))
    except Exception: prev = {'ngx': {}, 'global': {}}
    ngx, glob, notes = {}, {}, []
    try:
        for r in as_list(get_json(S('ngx_equities_url'))):
            if not isinstance(r, dict): continue
            sym = str(field(r, 'Symbol') or '').strip().upper()
            close, prevc = num(field(r, 'ClosePrice')), num(field(r, 'PrevClosingPrice'))
            p = close if close is not None else prevc
            if sym and p is not None: ngx[sym] = {'price': p, 'prev': prevc, 'date': iso(field(r, 'TradeDate'))}
        notes.append(f'{len(ngx)} NGX equities')
    except Exception as e: notes.append(f'equities failed: {e}')
    last = max([v['date'] for v in ngx.values() if v.get('date')] or [datetime.date.today().isoformat()])
    try:
        url = S('ngx_ticker_url')
        url += ('&' if '?' in url else '?') + urllib.parse.urlencode({'$filter': "TickerType  eq 'ETPS'"})
        n = 0
        for r in as_list(get_json(url)):
            if not isinstance(r, dict): continue
            sym = str(field(r, 'SYMBOL') or '').strip().upper()
            v, ch = num(field(r, 'Value')), num(field(r, 'PercChange'))
            if sym and v is not None: ngx[sym] = {'price': v, 'prev': (v - ch) if ch is not None else None, 'date': last}; n += 1
        notes.append(f'{n} ETPs')
    except Exception as e: notes.append(f'ETPs failed: {e}')
    try:
        latest = {}
        for r in as_list(get_json(S('fx_url'))):
            if not isinstance(r, dict): continue
            c = str(field(r, 'currency') or '').strip().upper()
            d = iso(str(field(r, 'ratedate') or '')[:10]); rate = num(field(r, 'centralrate'))
            if c and d and rate is not None and (c not in latest or latest[c][1] < d): latest[c] = (rate, d)
        U, G, E = latest.get('US DOLLAR'), latest.get('POUNDS STERLING'), latest.get('EURO')
        if U: glob['NGN=X'] = {'price': U[0], 'ccy': 'NGN', 'date': U[1]}
        if U and G: glob['GBPUSD=X'] = {'price': G[0] / U[0], 'ccy': 'USD', 'date': G[1]}
        if U and E: glob['EURUSD=X'] = {'price': E[0] / U[0], 'ccy': 'USD', 'date': E[1]}
        notes.append('CBN rates' if U else 'CBN: no US dollar rate')
    except Exception as e: notes.append(f'CBN failed: {e}')
    merged_ngx = {**prev.get('ngx', {}), **ngx}
    merged_glob = {**prev.get('global', {}), **glob}
    if not ngx and not glob:
        print('Nothing fetched – keeping the previous file.', notes); return 0
    data = {'generated_at': datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z', 'notes': '; '.join(notes), 'ngx': dict(sorted(merged_ngx.items())), 'global': merged_glob}
    with open(out_path, 'w', encoding='utf-8') as f: json.dump(data, f, separators=(',', ':'))
    print('prices.json written:', data['notes'])
    return 0

if __name__ == '__main__':
    sys.exit(main())
