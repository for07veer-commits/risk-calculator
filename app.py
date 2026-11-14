import streamlit as st

st.set_page_config(page_title="Auto Risk & Position Sizer", layout="centered")

st.title("📊 Auto Risk & Position Size Calculator")
st.markdown("Yeh app Entry Price dalte hi aapke Risk aur RR ratio ke hisab se automatic SL, TGT aur Quantity calculate karegi.")

# 1. Account Info
st.header("1. Account Details")
col1, col2 = st.columns(2)
with col1:
    total_capital = st.number_input("Total Capital (₹)", min_value=0.0, value=30000.0, step=1000.0)
with col2:
    risk_percentage = st.number_input("Risk Per Trade (%)", min_value=0.1, max_value=100.0, value=3.3, step=0.1)

max_risk_amount = total_capital * (risk_percentage / 100)
st.info(f"💡 Aap is trade mein maximum **₹{max_risk_amount:,.2f}** ka risk le rahe hain.")

# 2. Strategy Setup
st.header("2. Strategy Setup")
col3, col4 = st.columns(2)
with col3:
    sl_percent = st.number_input("Stop Loss Margin (%)", min_value=0.1, value=1.0, step=0.1, help="Entry price se SL kitne % door hona chahiye")
with col4:
    rr_ratio = st.number_input("Risk : Reward Ratio (1:X)", min_value=0.1, value=2.0, step=0.1, help="Agar 1:2 ka ratio chahiye toh 2 dalein")

# 3. Trade Entry
st.header("3. Trade Entry")
trade_type = st.radio("Trade Type:", ("Long (Buy)", "Short (Sell)"))
entry_price = st.number_input("Entry Price (₹) Type karein aur Enter dabayein", min_value=0.0, format="%.2f")

if entry_price > 0:
    # Calculations
    if trade_type == "Long (Buy)":
        sl_price = entry_price - (entry_price * (sl_percent / 100))
        risk_per_share = entry_price - sl_price
        tgt_price = entry_price + (risk_per_share * rr_ratio)
    else:
        sl_price = entry_price + (entry_price * (sl_percent / 100))
        risk_per_share = sl_price - entry_price
        tgt_price = entry_price - (risk_per_share * rr_ratio)
        
    quantity = int(max_risk_amount / risk_per_share) if risk_per_share > 0 else 0
    total_invested = quantity * entry_price
    total_profit = quantity * (abs(tgt_price - entry_price))

    # Display Results automatically
    st.success("✅ **Auto Calculation Successful!**")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Entry Price", f"₹ {entry_price:,.2f}")
    c2.metric("Auto Stop Loss (SL)", f"₹ {sl_price:,.2f}")
    c3.metric("Auto Target (TGT)", f"₹ {tgt_price:,.2f}")
    
    st.divider()
    
    c4, c5 = st.columns(2)
    with c4:
        st.metric("Total Quantity (Shares)", f"{quantity}")
        st.metric("Capital Required", f"₹ {total_invested:,.2f}")
    with c5:
        st.metric("Total Risk (Potential Loss)", f"₹ {quantity * risk_per_share:,.2f}")
        st.metric("Potential Profit", f"₹ {total_profit:,.2f}")
