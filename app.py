import streamlit as st
import plotly.graph_objects as go

# Page config
st.set_page_config(page_title="CO₂ & ROI Dashboard", layout="wide")

# --- Sidebar Currency ---
currency_options = {"USD": "$", "SGD": "S$", "MYR": "RM", "IDR": "Rp", "HKD": "HK$", "RMB": "¥"}
st.sidebar.markdown("### 💱 Currency")
selected_currency = st.sidebar.selectbox("Select Currency", options=list(currency_options.keys()), index=1)
currency_symbol = f"$ {selected_currency}"

# --- Country Carbon Factors (kg CO2/kWh) ---
country_factors = {
    "Indonesia": 0.87, "Singapore": 0.408, "Malaysia": 0.585,
    "Thailand": 0.513, "Vietnam": 0.618, "Philippines": 0.65,
    "China": 0.555, "Japan": 0.474, "South Korea": 0.405,
    "India": 0.82, "Australia": 0.79, "United States": 0.42,
    "United Kingdom": 0.233, "Germany": 0.338, "Custom": None
}

# --- Input Parameters ---
st.header("🔧 Input Parameters")
col1, col2, col3 = st.columns(3)

with col1:
    energy_savings = st.number_input("Estimated Energy Savings (kWh/year)", value=1040249.0)
    electricity_rate = st.number_input(f"Electricity Rate ({currency_symbol}/kWh)", value=0.14)

with col2:
    selected_country = st.selectbox("Select Country", list(country_factors.keys()))
    carbon_emission_factor = (st.number_input("Custom CO₂ Factor (kg/kWh)", value=0.82)
                              if selected_country == "Custom"
                              else country_factors[selected_country])

    savings_pct = st.number_input("Potential Energy Savings (%)", value=8.8, format="%.2f") / 100

with col3:
    initial_investment = st.number_input(f"Initial Investment ({currency_symbol})", value=16000.0)
    software_fee = st.number_input(f"Annual SaaS Fee ({currency_symbol})", value=72817.0)
    roi_years = st.selectbox("ROI Duration (Years)", options=[3, 5])

# --- Derived Calculations ---
total_energy_before = energy_savings / savings_pct if savings_pct > 0 else 0
energy_after = total_energy_before - energy_savings
annual_savings = energy_savings * electricity_rate
carbon_reduction = energy_savings * carbon_emission_factor

# --- Payback Calculation ---
if annual_savings > software_fee:
    payback = initial_investment / (annual_savings - software_fee)
    payback_text = f"{payback:.2f} yrs"
else:
    payback_text = "Not achievable"

# --- Metrics Summary (One Line) ---
st.markdown("### 📊 Summary Metrics")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Carbon Reduction", f"{carbon_reduction / 1000:.1f} tCO₂e/year")
m2.metric("Energy Savings", f"{energy_savings/1000:,.0f}k kWh/year")
m3.metric("Savings %", f"{savings_pct * 100:.1f}%")
m4.metric("Payback Period", payback_text)

# --- ROI Chart ---
st.subheader(f"💰 {roi_years}-Year ROI Forecast")

total_costs = [initial_investment + software_fee] + [software_fee] * (roi_years - 1)
cumulative_savings = []
net_cash_flow = []
for i in range(roi_years):
    net = annual_savings - total_costs[i]
    net_cash_flow.append(net if i == 0 else net_cash_flow[-1] + net)
    cumulative_savings.append(net_cash_flow[-1])

fig = go.Figure()
fig.add_trace(go.Bar(x=list(range(roi_years)), y=[annual_savings]*roi_years,
                     name="Annual Savings", marker_color="green"))
fig.add_trace(go.Bar(x=list(range(roi_years)), y=total_costs,
                     name="Investment", marker_color="red"))
fig.add_trace(go.Scatter(x=list(range(roi_years)), y=cumulative_savings,
                         mode="lines+markers", name="Cumulative Net Savings", line=dict(color="blue")))

fig.update_layout(
    barmode='group',
    height=400,
    xaxis_title='Year',
    yaxis_title=f'Cash Flow ({currency_symbol})',
    plot_bgcolor='white',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=20, r=20, t=30, b=30)
)

st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# --- Footer ---
st.markdown("---")
st.caption("Crafted by Univers AI • Internal Use Only • Powered by Streamlit")
