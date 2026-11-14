import streamlit as st

st.set_page_config(page_title="Risk & Position Sizer", layout="centered")

st.title("📊 Trading Risk & Position Size Calculator")
st.markdown("Yeh app aapko batayegi ki aapko kitni quantity leni chahiye aur trade mein kitna paisa lagana chahiye.")

# 1. Account Info
st.header("1. Account Details")
total_capital = st.number_input("Total Capital / Amount (₹)", min_value=0.0, value=100000.0, step=1000.0)
risk_percentage = st.number_input("Risk Per Trade (%)", min_value=0.1, max_value=100.0, value=1.0, step=0.1)

# Calculate max risk amount
max_risk_amount = total_capital * (risk_percentage / 100)
st.info(f"💡 Aap is trade mein maximum **₹{max_risk_amount:,.2f}** ka risk le rahe hain.")

# 2. Trade Details
st.header("2. Trade Setup")
trade_type = st.radio("Trade Type:", ("Long (Buy)", "Short (Sell)"))

col1, col2, col3 = st.columns(3)
with col1:
    entry_price = st.number_input("Entry Price (₹)", min_value=0.0, format="%.2f")
with col2:
    sl_price = st.number_input("Stop Loss (SL) (₹)", min_value=0.0, format="%.2f")
with col3:
    tgt_price = st.number_input("Target (TGT) (₹)", min_value=0.0, format="%.2f")

# 3. Calculation & Output
if st.button("Calculate Position", use_container_width=True):
    if entry_price == 0 or sl_price == 0:
        st.error("⚠️ Entry aur Stop Loss price 0 nahi ho sakte!")
    elif entry_price == sl_price:
        st.error("⚠️ Entry aur Stop Loss price same nahi ho sakte!")
    else:
        # Risk per share calculation
        if trade_type == "Long (Buy)":
            risk_per_share = entry_price - sl_price
            profit_per_share = tgt_price - entry_price if tgt_price > 0 else 0
        else:
            risk_per_share = sl_price - entry_price
            profit_per_share = entry_price - tgt_price if tgt_price > 0 else 0

        if risk_per_share <= 0:
            st.error("⚠️ Stop Loss galat lagaya hai! Long trade mein SL Entry se chota hota hai, aur Short mein bada.")
        else:
            # Main Calculations
            quantity = int(max_risk_amount / risk_per_share)
            total_invested = quantity * entry_price
            total_profit = quantity * profit_per_share
            
            if tgt_price > 0 and profit_per_share > 0:
                rr_ratio = profit_per_share / risk_per_share
            else:
                rr_ratio = 0

            # Display Results
            st.success("✅ **Calculation Successful!**")
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Total Quantity (Shares)", f"{quantity}")
                st.metric("Capital Required", f"₹ {total_invested:,.2f}")
            with c2:
                st.metric("Total Risk (Potential Loss)", f"₹ {quantity * risk_per_share:,.2f}")
                st.metric("Potential Profit (At Target)", f"₹ {total_profit:,.2f}")
                
            st.divider()
            if rr_ratio > 0:
                st.markdown(f"**Risk : Reward Ratio = 1 : {rr_ratio:.2f}**")
                if rr_ratio >= 2:
                    st.success("TGT aur SL ka ratio achha hai (1:2 ya usse zyada). Good Trade!")
                else:
                    st.warning("TGT aur SL ka ratio 1:2 se kam hai. Risk zyada hai aur profit kam.")
