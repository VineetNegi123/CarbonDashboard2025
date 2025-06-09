import streamlit as st
import plotly.graph_objects as go

# Page setup
st.set_page_config(page_title="CO₂ & ROI Dashboard", layout="wide")

# Currency selection
currency_options = {"USD": "$", "SGD": "S$", "MYR": "RM", "IDR": "Rp", "HKD": "HK$", "RMB": "¥"}
st.sidebar.markdown("### 💱 Currency")
selected_currency = st.sidebar.selectbox("Select Currency", list(currency_options.keys()), index=1)
currency_symbol = f"$ {selected_currency}"

# Country carbon factors (kg CO₂/kWh)
country_factors = {
    "Indonesia": 0.87, "Singapore": 0.408, "Malaysia": 0.585, "Thailand": 0.513,
    "Vietnam": 0.618, "Philippines": 0.65, "China": 0.555, "Japan": 0.474,
    "South Korea": 0.405, "India": 0.82, "Australia": 0.79, "United States": 0.42,
    "United Kingdom": 0.233, "Germany": 0.338, "Custom": None
}

# Input section
st.header("🔧 Input Parameters")
col1, col2, col3 = st.columns(3)

with col1:
    energy_savings = st.number_input("Estimated Energy Savings (kWh/year)", value=1040249.0)
    electricity_rate = st.number_input(f"Electricity Rate ({currency_symbol}/kWh)", value=0.14)
    cooling_energy = st.number_input("Cooling Energy (RTh/year)", value=21900000)

with col2:
    selected_country = st.selectbox("Select Country", list(country_factors.keys()))
    carbon_emission_factor = st.number_input("Custom CO₂ Factor (kg/kWh)", value=0.82) \
        if selected_country == "Custom" else country_factors[selected_country]
    efficiency_pct = st.number_input("Efficiency Improvement (%)", value=5.0, format="%.2f") / 100

with col3:
    initial_investment = st.number_input(f"Initial Investment ({currency_symbol})", value=16000.0)
    software_fee = st.number_input(f"Annual SaaS Fee ({currency_symbol})", value=72817.0)
    roi_years = st.selectbox("ROI Duration (Years)", options=[3, 5])

# --- Final Payback Formula Using Energy Savings Input ---
carbon_reduction = energy_savings * carbon_emission_factor
annual_savings = energy_savings * electricity_rate
total_investment = initial_investment + software_fee

payback_text = (
    f"{total_investment / annual_savings:.2f} yrs"
    if annual_savings > 0 else "Not achievable"
)

# --- Summary Metrics Display ---
st.markdown("""
<h3>📊 Summary Metrics</h3>
<style>
.summary-metric {{
    display: flex;
    justify-content: space-between;
    gap: 30px;
    margin-top: 10px;
    margin-bottom: 30px;
}}
.summary-box {{
    background-color: #f9f9f9;
    padding: 14px 20px;
    border-radius: 10px;
    width: 100%;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}}
.summary-value {{
    font-size: 20px;
    font-weight: 600;
}}
.summary-label {{
    font-size: 14px;
    color: #666;
    margin-top: 4px;
}}
</style>
<div class="summary-metric">
    <div class="summary-box">
        <div class="summary-value">{:.1f} tCO₂e/year</div>
        <div class="summary-label">Carbon Reduction</div>
    </div>
    <div class="summary-box">
        <div class="summary-value">{:,} kWh/year</div>
        <div class="summary-label">Energy Savings</div>
    </div>
    <div class="summary-box">
        <div class="summary-value">{:.1f}%</div>
        <div class="summary-label">Efficiency Improvement</div>
    </div>
    <div class="summary-box">
        <div class="summary-value">{}</div>
        <div class="summary-label">Payback Period</div>
    </div>
</div>
""".format(
    carbon_reduction / 1000,
    int(energy_savings),
    efficiency_pct * 100,
    payback_text
), unsafe_allow_html=True)

# --- ✅ Corrected ROI Forecast ---
st.subheader(f"💰 {roi_years}-Year ROI Forecast")

# Build cost and savings arrays
annual_savings_list = [annual_savings] * roi_years
investment_costs = [initial_investment + software_fee] + [software_fee] * (roi_years - 1)

# Compute cumulative savings and net cash
cumulative_savings = []
net_cash_flow = []

for i in range(roi_years):
    net = annual_savings_list[i] - investment_costs[i]
    net_cash_flow.append(net if i == 0 else net_cash_flow[-1] + net)
    cumulative_savings.append(net_cash_flow[-1])

# Create the chart
fig = go.Figure()
fig.add_trace(go.Bar(
    x=list(range(roi_years)),
    y=annual_savings_list,
    name="Annual Savings",
    marker_color="green"
))
fig.add_trace(go.Bar(
    x=list(range(roi_years)),
    y=investment_costs,
    name="Investment",
    marker_color="red"
))
fig.add_trace(go.Scatter(
    x=list(range(roi_years)),
    y=cumulative_savings,
    mode="lines+markers",
    name="Cumulative Net Savings",
    line=dict(color="blue")
))

fig.update_layout(
    barmode='group',
    height=400,
    xaxis=dict(title='Year', range=[0, roi_years - 1]),  # No -0.5 offset
    yaxis_title=f'Cash Flow ({currency_symbol})',
    plot_bgcolor='white',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=20, r=20, t=30, b=30)
)

st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# --- Notes ---
st.markdown("---")
st.subheader("📝 Notes")
st.markdown("""
- Savings are indicative only and assume 12 months of clean interval energy + HVAC data; we will recalculate once verified data is available.
- We assume your BMS offers read/write API access with documented point names and units; exact scope and timeline will be set after we review the point list.
- Models use current schedules, set-points and occupancy; any major change (new tenants, longer hours, etc.) will shift both baseline and savings.
- Cost and CO₂ figures use prevailing market values.
- No new meters, controllers, network upgrades or cybersecurity work are included; any required additions will be separately scoped and priced after a joint site survey.
""")

st.caption("Crafted by Univers AI • For Proposal Use Only • Powered by Streamlit")
