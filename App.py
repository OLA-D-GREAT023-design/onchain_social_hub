import streamlit as st
import main

st.set_page_config(page_title="Onchain Social Hub", layout="wide")
st.markdown("<style>.main{background:#0e1117;color:#fff}.stTextInput>div>input{background:#1e1e1e;color:#fff;border:1px solid #ff6b35}.stButton>button{background:#ff6b35;color:#fff;border-radius:5px}</style>", unsafe_allow_html=True)

st.title("Onchain Social Hub")
st.markdown("*Your wallet = your social profile.*")

with st.sidebar:
    st.header("API Key")
    key = st.text_input("Zerion API Key", type="password", help="zerion.io/api")
    if not key: st.warning("Enter key"); st.stop()

wallets = st.text_area("Wallets (one per line)", "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045\n0xab5801a7D398351b8bE11C439e05C5B3259aeC9B", height=100).strip().split("\n")
wallets = [w.strip() for w in wallets if w.strip()]

if st.button("Scan", type="primary") and wallets:
    with st.spinner("Scanning..."):
        result = main.run(wallets, key)
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

    if result["communities"]:
        st.subheader("Communities")
        for k, v in result["communities"].items():
            st.info(f"{k}: {len(v)} wallets")
            st.write(v)
    else:
        st.info("No shared assets found.")

    st.markdown(f"**{result['summary']}**")
