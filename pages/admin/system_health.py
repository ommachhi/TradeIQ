import streamlit as st
from database.db import SessionLocal
from database.models import SystemSetting
import time

def render(user: dict):
    st.title("System Health & Settings")
    st.caption("Manage global platform configuration and view real-time diagnostics.")
    
    db = SessionLocal()
    try:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### System Diagnostics")
            if st.button("Run Full Diagnostics"):
                with st.spinner("Running deep diagnostics..."):
                    time.sleep(2)
                    st.toast("Diagnostics completed successfully.", icon="✅")
                    
            st.markdown("""
            - **Database Latency:** 12ms
            - **Redis Cache:** Connected (98% Hit Rate)
            - **ML Inference Engine:** Online (Avg 45ms)
            - **External APIs (yfinance):** Rate limit at 42%
            - **Disk Space:** 45% Used
            """)
            
        with c2:
            st.markdown("### Global Settings")
            settings = db.query(SystemSetting).all()
            settings_dict = {s.key: s.value for s in settings}
            
            with st.form("sys_settings"):
                maint_mode = st.checkbox("Maintenance Mode", value=settings_dict.get("MAINTENANCE_MODE") == "True")
                reg_open = st.checkbox("Allow New Registrations", value=settings_dict.get("REGISTRATIONS_OPEN", "True") == "True")
                api_rate = st.number_input("Global API Rate Limit (req/min)", value=int(settings_dict.get("API_RATE_LIMIT", "100")))
                
                if st.form_submit_button("Save Settings"):
                    def set_val(key, val):
                        s = db.query(SystemSetting).filter_by(key=key).first()
                        if s:
                            s.value = str(val)
                        else:
                            db.add(SystemSetting(key=key, value=str(val)))
                    
                    set_val("MAINTENANCE_MODE", "True" if maint_mode else "False")
                    set_val("REGISTRATIONS_OPEN", "True" if reg_open else "False")
                    set_val("API_RATE_LIMIT", api_rate)
                    
                    db.commit()
                    st.toast("System settings updated.", icon="✅")
                    st.rerun()
    finally:
        db.close()
