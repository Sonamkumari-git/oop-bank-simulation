import streamlit as st
import requests
import pandas as pd
import time
import os

# Cloud (Render) par API_URL set karenge, nahi toh local 8000 use karega
BASE_URL = "https://oop-bank-simulation.onrender.com"

st.set_page_config(page_title="Apex Secure Internet Banking", page_icon="🏦", layout="wide")

# Session State Management
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "customer_id" not in st.session_state: st.session_state.customer_id = None
if "customer_name" not in st.session_state: st.session_state.customer_name = None

# Sidebar Logout
if st.session_state.logged_in:
    st.sidebar.markdown(f"### 👤 Welcome, **{st.session_state.customer_name}**")
    st.sidebar.caption(f"Secure Session ID: {st.session_state.customer_id}")
    if st.sidebar.button("🔒 Secure Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# --- LOGIN / SIGNUP GATEWAY ---
if not st.session_state.logged_in:
    st.title("🏦 Apex Global Net-Banking Terminal")
    tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 Open New Digital Profile"])
    
    with tab1:
        login_id = st.text_input("Enter Customer Security ID:", key="login_id")
        if st.button("Verify & Access Dashboard", use_container_width=True):
            try:
                res = requests.post(f"{BASE_URL}/auth/login", json={"customer_id": login_id})
                if res.status_code == 200:
                    st.session_state.logged_in = True
                    st.session_state.customer_id = res.json()["customer_id"]
                    st.session_state.customer_name = res.json()["name"]
                    st.toast("Security Cleared! Redirecting...", icon="🔓")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(res.json().get("detail", "Invalid credentials."))
            except Exception as e:
                st.error("🚨 API Server is down or unreachable.")
                
    with tab2:
        reg_id = st.text_input("Create Custom User ID:", placeholder="e.g., ROHAN7")
        reg_name = st.text_input("Your Legal Full Name:")
        if st.button("Register Profile", use_container_width=True):
            res = requests.post(f"{BASE_URL}/auth/signup", json={"customer_id": reg_id, "name": reg_name})
            if res.status_code == 200:
                st.success("Registration completed successfully! Please login.")
            else:
                st.error(res.json().get("detail", "Registration Failed."))

# --- TRUE BANKING DASHBOARD ---
else:
    st.markdown(f"# 🏛️ APEX NET-BANKING PORTAL")
    st.write("🔒 256-bit SSL Encrypted Transaction Environment")
    st.markdown("---")
    
    acc_res = requests.get(f"{BASE_URL}/customers/{st.session_state.customer_id}/accounts")
    accounts_list = acc_res.json() if acc_res.status_code == 200 else []
    
    if not accounts_list:
        st.warning("No active accounts found.")
        st.markdown("### Open an Account")
        acc_type = st.selectbox("Account Type", ["SAVINGS", "CURRENT"])
        init_dep = st.number_input("Initial Deposit", min_value=0.0)
        if st.button("Open Account"):
            res = requests.post(f"{BASE_URL}/customers/{st.session_state.customer_id}/accounts/open", json={"account_type": acc_type, "initial_balance": init_dep})
            if res.status_code == 200:
                st.success("Account Opened!")
                time.sleep(1)
                st.rerun()
    else:
        account_options = [acc["account_number"] for acc in accounts_list]
        col_left, col_right = st.columns([2, 1])
        
        with col_right:
            st.markdown("### 💳 Selected Asset Profile")
            selected_acc = st.selectbox("Choose Active Account:", account_options)
            active_acc = next(acc for acc in accounts_list if acc["account_number"] == selected_acc)
            
            st.markdown(f"""
            <div style='background-color:#1E1E2F; padding:20px; border-radius:15px; border-left: 5px solid #00FFCC;'>
                <p style='color:#888899; margin:0; font-size:14px;'>AVAILABLE BALANCE</p>
                <h1 style='color:#FFFFFF; margin:5px 0; font-size:36px;'>₹{active_acc['balance']:,.2f}</h1>
                <p style='color:#00FFCC; margin:0; font-size:12px;'>Type: {active_acc['account_type']}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_left:
            st.markdown("### 🔄 Quick Financial Operations")
            op_tab, transfer_tab, statement_tab = st.tabs(["💵 Self Deposit/Withdraw", "💸 Fund Transfer", "📜 E-Statement"])
            
            with op_tab:
                action_type = st.radio("Choose Action:", ["Deposit", "Withdrawal"])
                amount = st.number_input("Enter Amount (₹):", min_value=0.0, step=500.0)
                
                if st.button("Proceed Transaction", use_container_width=True):
                    if amount <= 0:
                        st.warning("Please enter a valid amount.")
                    else:
                        with st.spinner("Connecting to Secure Core Banking Server..."):
                            endpoint = "deposit" if action_type == "Deposit" else "withdraw"
                            res = requests.post(f"{BASE_URL}/accounts/{selected_acc}/{endpoint}", json={"amount": amount})
                            
                            if res.status_code == 200:
                                st.success(f"🎉 Success! New Balance: ₹{res.json()['new_balance']:,.2f}")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"Failed: {res.json().get('detail')}")
                                
            with transfer_tab:
                target_acc_input = st.text_input("Enter Beneficiary Account Number:")
                transfer_amount = st.number_input("Enter Transfer Amount (₹):", min_value=0.0, step=500.0, key="trans_amt")
                
                if st.button("🚀 Transfer Funds securely", use_container_width=True):
                    if not target_acc_input or transfer_amount <= 0:
                        st.error("Please enter valid details.")
                    else:
                        with st.spinner("Authorizing Transfer..."):
                            res = requests.post(f"{BASE_URL}/accounts/{selected_acc}/transfer", 
                                                json={"target_account": target_acc_input, "amount": transfer_amount})
                            if res.status_code == 200:
                                st.success("Transfer Settled Successfully!")
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error(f"❌ Transfer Failed: {res.json().get('detail')}")

            with statement_tab:
                stmt_res = requests.get(f"{BASE_URL}/accounts/{selected_acc}/statement")
                if stmt_res.status_code == 200 and stmt_res.json():
                    df = pd.DataFrame(stmt_res.json())
                    # Format timestamp if it exists
                    if 'created_at' in df.columns:
                        df.rename(columns={'created_at': 'Execution Timestamp'}, inplace=True)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.caption("No financial transaction ledger entries found.")
