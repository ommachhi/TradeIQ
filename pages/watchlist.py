import streamlit as st
import pandas as pd
from database.db import SessionLocal
from database.models import Watchlist
from services.market_data import get_stock_quote, INDIAN_STOCKS
from utils.formatting import format_inr

def render(user: dict):
    st.title("Watchlist")
    st.caption("Monitor your favourite stocks.")
    
    db = SessionLocal()
    try:
        if st.session_state.get("wl_add"):
            sym = st.session_state["wl_add"]
            exists = db.query(Watchlist).filter_by(user_id=user['id'], symbol=sym).first()
            if exists:
                st.warning("Already in watchlist.")
            else:
                db.add(Watchlist(user_id=user['id'], symbol=sym))
                db.commit()
                st.success("Added to watchlist.")
            del st.session_state["wl_add"]
            st.rerun()

        if st.session_state.get("wl_del"):
            w_id = st.session_state["wl_del"]
            w = db.query(Watchlist).get(w_id)
            if w and w.user_id == user['id']:
                db.delete(w)
                db.commit()
            del st.session_state["wl_del"]
            st.rerun()

        with st.form("add_wl"):
            sym = st.selectbox("Add to Watchlist", options=list(INDIAN_STOCKS.keys()))
            if st.form_submit_button("Add"):
                st.session_state["wl_add"] = sym
                st.rerun()
                
        wl = db.query(Watchlist).filter_by(user_id=user['id']).all()
        if not wl:
            st.info("Your watchlist is empty.")
        else:
            rows = []
            for w in wl:
                q = get_stock_quote(w.symbol)
                if q:
                    rows.append({
                        "ID": w.id,
                        "Symbol": w.symbol,
                        "Company": q['company'],
                        "Current Price": format_inr(q['price']),
                        "Change": f"{'+' if q['change']>0 else ''}{q['change']:.2f}",
                        "Change%": f"{'+' if q['change_pct']>0 else ''}{q['change_pct']:.2f}%"
                    })
            if rows:
                st.dataframe(pd.DataFrame(rows).drop(columns=["ID"]), use_container_width=True)
                for r in rows:
                    if st.button(f"Remove {r['Symbol']}", key=f"del_wl_{r['ID']}"):
                        st.session_state["wl_del"] = r['ID']
                        st.rerun()
    finally:
        db.close()
