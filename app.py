import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Live Auto Risk & Position Sizer", layout="centered")

st.title("🌍 Live Global Risk & Position Sizer")
st.markdown("Search bar se Spot price dekhein, aur apne **Option Premium** par exact Quantity calculate karein.")

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
st.header("2. Strategy & Instrument Setup")
col3, col4, col_lot = st.columns(3)
with col3:
    sl_percent = st.number_input("Stop Loss Margin (%)", min_value=0.1, value=1.0, step=0.1)
with col4:
    rr_ratio = st.number_input("Risk : Reward (1:X)", min_value=0.1, value=2.0, step=0.1)
with col_lot:
    lot_size = st.number_input("Lot Size (Qty in 1 Lot)", min_value=1, value=65, step=1)

# 3. LIVE SEARCH BAR (Spot / Index Price)
st.header("3. 🔍 Live Index / Spot Price")
POPULAR_TICKERS = {
    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "Reliance Industries": "RELIANCE.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "State Bank of India (SBI)": "SBIN.NS",
    "Infosys": "INFY.NS",
    "Tata Motors": "TATAMOTORS.NS",
    "Apple (US)": "AAPL",
    "--- Type Custom Symbol ---": "CUSTOM"
}

search_col, live_col = st.columns([2, 1])
with search_col:
    selected_name = st.selectbox("Naam Type karein aur select karein:", list(POPULAR_TICKERS.keys()))
    if POPULAR_TICKERS[selected_name] == "CUSTOM":
        symbol = st.text_input("Custom Symbol dalein (eg: TATAPOWER.NS):", "TATAPOWER.NS")
    else:
        symbol = POPULAR_TICKERS[selected_name]
        st.caption(f"Backend Symbol: {symbol}")
    
live_price = 0.0
if symbol:
    try:
        with st.spinner("Fetching Live Price..."):
            ticker = yf.Ticker(symbol.upper())
            data = ticker.history(period="1d")
            if not data.empty:
                live_price = data['Close'].iloc[-1]
                with live_col:
                    st.success(f"Spot / Index LTP:\n### ₹ {live_price:,.2f}")
            else:
                st.error("Symbol nahi mila! Sahi naam dalein.")
    except Exception as e:
        st.error("Error fetching data.")

# 4. Trade Entry & Calculation (With Option Strike Columns)
st.header("4. Trade Entry (Options / Stock)")

col_t1, col_t2 = st.columns(2)
with col_t1:
    trade_type = st.radio("Trade Type:", ("Long (Buy)", "Short (Sell)"))
with col_t2:
    leverage = st.number_input("Intraday Margin/Leverage (1 for Options)", min_value=1, value=1, step=1)

st.markdown("### 📝 Enter Strike & Premium")
col_e1, col_e2 = st.columns(2)
with col_e1:
    # Naya column Strike Name ke liye
    strike_name = st.text_input("Option Strike Name (Eg: 25100 CE)", placeholder="Eg: 25100 CE")
with col_e2:
    # Naya column Option Premium ke liye (ispar SL aur Target calculate hoga)
    entry_price = st.number_input("Entry Price / Option Premium (₹)", min_value=0.0, value=0.0, format="%.2f", help="Option ka premium ya stock ka entry price dalein")

if entry_price > 0:
    if trade_type == "Long (Buy)":
        sl_price = entry_price - (entry_price * (sl_percent / 100))
        risk_per_share = entry_price - sl_price
        tgt_price = entry_price + (risk_per_share * rr_ratio)
    else:
        sl_price = entry_price + (entry_price * (sl_percent / 100))
        risk_per_share = sl_price - entry_price
        tgt_price = entry_price - (risk_per_share * rr_ratio)
        
    if risk_per_share > 0:
        qty_by_risk = int(max_risk_amount / risk_per_share)
        buying_power = total_capital * leverage
        qty_by_capital = int(buying_power / entry_price)
        
        final_raw_qty = min(qty_by_risk, qty_by_capital)
        no_of_lots = int(final_raw_qty / lot_size)
        total_shares = no_of_lots * lot_size
    else:
        final_raw_qty, no_of_lots, total_shares = 0, 0, 0

    total_invested = total_shares * entry_price
    actual_risk = total_shares * risk_per_share
    total_profit = total_shares * (abs(tgt_price - entry_price))

    if total_shares == 0:
        st.error(f"⚠️ Aapke Capital (₹{total_capital}) mein is premium (₹{entry_price}) par 1 Lot aana mumkin nahi hai, ya Risk limit bohot kam hai.")
    else:
        st.success(f"✅ **Calculation Successful for {strike_name if strike_name else 'Trade'}!**")
        c1, c2, c3 = st.columns(3)
        c1.metric("Premium / Entry", f"₹ {entry_price:,.2f}")
        c2.metric("Stop Loss (SL)", f"₹ {sl_price:,.2f}")
        c3.metric("Target (TGT)", f"₹ {tgt_price:,.2f}")
        
        st.divider()
        
        st.markdown("### 📦 Exact Position Sizing")
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Lot Size", f"{lot_size}")
        col_b.metric("No. of Lots", f"{no_of_lots} Lots")
        col_c.metric("Total Shares (Qty)", f"{total_shares}")

        st.divider()
        
        c4, c5 = st.columns(2)
        with c4:
            st.metric("Capital Required (₹)", f"₹ {total_invested:,.2f}")
        with c5:
            st.metric("Total Risk (Loss)", f"₹ {actual_risk:,.2f}")
            
        st.info(f"💰 **Potential Profit (At Target): ₹ {total_profit:,.2f}**")
