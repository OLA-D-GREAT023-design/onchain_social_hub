import requests, time
from collections import defaultdict

BASE = "https://api.zerion.io/v1"

def fetch(url, params, headers):
    while True:
        r = requests.get(url, headers=headers, params=params).json()
        yield from r.get("data", [])
        token = r.get("meta", {}).get("next_page_token")
        if not token: break
        params["page[token]"] = token
        time.sleep(0.2)

def portfolio(addr, headers):
    if not (addr.startswith("0x") and len(addr) == 42):
        raise ValueError("Invalid address")
    r = requests.get(f"{BASE}/wallets/{addr}/portfolio", headers=headers, params={"currency": "usd"}).json()
    v = r["data"]["attributes"].get("total_value", 0)
    a = [p["id"] for p in r["data"]["relationships"]["positions"]["data"]]
    return v, a

def tx_count(addr, headers):
    return sum(1 for _ in fetch(f"{BASE}/wallets/{addr}/transactions", {"limit": 100}, headers))

def profile(addr, headers):
    v, a = portfolio(addr, headers)
    t = tx_count(addr, headers)
    return {
        "wallet": addr,
        "value_usd": round(v, 2),
        "tx_count": t,
        "assets": len(a),
        "score": round(t * 10 + v / 100 + len(a) * 5, 2),
        "top": a[:3]
    }

def communities(wallets, headers):
    h = {}
    for w in wallets:
        try: _, a = portfolio(w, headers); h[w] = set(a)
        except: pass
    g = defaultdict(list)
    for i, a in enumerate(h):
        for b in list(h)[i+1:]:
            c = h[a] & h[b]
            if len(c) >= 2:
                k = ", ".join(sorted(c)[:3]) + ("..." if len(c) > 3 else "")
                g[k].extend([a, b])
    return {k: list(dict.fromkeys(v)) for k, v in g.items()}

def run(wallets, key):
    headers = {"Authorization": f"Bearer {key}"}
    profiles = {}
    for w in wallets:
        try: profiles[w] = profile(w, headers)
        except Exception as e: profiles[w] = {"error": str(e)}
    comm = communities(wallets, headers)
    return {"profiles": profiles, "communities": comm, "summary": f"{len(comm)} group(s)"}
