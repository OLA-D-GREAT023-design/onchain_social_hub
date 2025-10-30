import streamlit as st
import requests, time

st.set_page_config(page_title="Onchain Social Hub", layout="wide")
st.markdown("<style>.main{background:#0e1117;color:#fff}.stTextInput>div>input{background:#1e1e1e;color:#fff;border:1px solid #ff6b35}.stButton>button{background:#ff6b35;color:#fff;border-radius:5px}</style>", unsafe_allow_html=True)

st.title("Onchain Social Hub")
st.markdown("*Your wallet = your social profile.*")

with st.sidebar:
    st.header("API Key")
    key = st.text_input("Zerion API Key", type="password", help="zerion.io/api")
    if not key: st.warning("Enter key"); st.stop()

wallets = st.text_area("Wallets (one per line)", "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045", height=100).strip().split("\n")
wallets = [w.strip() for w in wallets if w.strip()]

if st.button("Scan", type="primary") and wallets:
    headers = {"Authorization": f"Bearer {key}"}
    with st.spinner("Scanning..."):
        profiles = {}
        for addr in wallets:
            try:
                if not (addr.startswith("0x") and len(addr) == 42):
                    profiles[addr] = {"error": "Invalid wallet address"}
                    continue
                p_url = f"https://api.zerion.io/v1/wallets/{addr}/portfolio?currency=usd"
                p_r = requests.get(p_url, headers=headers, timeout=10).json()
                if "data" not in p_r:
                    profiles[addr] = {"error": "No data (inactive wallet?)"}
                    continue
                v = p_r["data"]["attributes"].get("total_value", 0)
                a = [pos["id"] for pos in p_r["data"]["relationships"]["positions"]["data"]]
                t_url = f"https://api.zerion.io/v1/wallets/{addr}/transactions?limit=100"
                t_r = requests.get(t_url, headers=headers, timeout=10).json()
                t = len(t_r.get("data", []))
                score = t * 10 + v / 100 + len(a) * 5
                profiles[addr] = {"value_usd": round(v, 2), "tx_count": t, "assets": len(a), "score": round(score, 2), "top": a[:3]}
            except Exception as e:
                profiles[addr] = {"error": str(e)}
        
        result = {"profiles": profiles, "summary": f"Scanned {len(wallets)} wallets"}

    st.success("Done!")
    for w, p in result["profiles"].items():
        if "error" in p:
            st.error(f"{w[:10]}...: {p['error']}")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Value", f"${p['value_usd']:,}")
            c2.metric("Txs", p['tx_count'])
            c3.metric("Score", p['score'])
            with st.expander(f"Top Assets: {w[:10]}..."): st.write(p['top'])
    st.markdown(f"**{result['summary']}**")
