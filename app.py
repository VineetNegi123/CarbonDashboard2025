import streamlit as st
import plotly.graph_objects as go

def compute_payback_year(cashflows):
    cumulative = 0
    for i in range(1, len(cashflows)):
        prev = cumulative
        cumulative += cashflows[i]
        if cumulative >= 0:
            return i - 1 + (-prev) / (cashflows[i])
    return None

# Page setup
st.set_page_config(page_title="CO₂ & ROI Dashboard", layout="wide")

# Currency selection
currency_options = {"USD": "$", "SGD": "S$", "MYR": "RM", "IDR": "Rp", "HKD": "HK$", "RMB": "¥"}
st.sidebar.markdown("### 💱 Currency")
selected_currency = st.sidebar.selectbox("Select Currency", list(currency_options.keys()), index=1)
currency_symbol = f"$ {selected_currency}"

# Carbon factors
country_factors = {
    "Indonesia": 0.87, "Singapore": 0.408, "Malaysia": 0.585, "Thailand": 0.513,
    "Vietnam": 0.618, "Philippines": 0.65, "China": 0.555, "Japan": 0.474,
    "South Korea": 0.405, "India": 0.82, "Australia": 0.79, "United States": 0.42,
    "United Kingdom": 0.233, "Germany": 0.338, "Custom": None
}

# Input UI
st.header("🛠️ Input Parameters")
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
    initial_investment = st.number_input(f"Initial Investment ({currency_symbol})", value=88817.0)
    one_time_install = st.number_input(f"One-Time Installation ({currency_symbol})", value=16000.0)
    software_fee = st.number_input(f"Annual SaaS Fee ({currency_symbol})", value=72817.0)
    roi_years = st.selectbox("ROI Duration (Years)", options=[3, 5])

# Calculations
carbon_reduction = energy_savings * carbon_emission_factor
annual_savings = energy_savings * electricity_rate

payback_text = (
    f"{initial_investment / annual_savings:.2f} yrs"
    if annual_savings > 0 else "Not achievable"
)

# Summary Metrics
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

# ROI CHART
st.subheader(f"💰 {roi_years}-Year ROI Forecast")

x_years = list(range(roi_years))
initials = [initial_investment] + [0]*(roi_years - 1)
fees = [0] + [software_fee] * (roi_years - 1)
savings = [annual_savings] * roi_years
net_flows = [s - f - i for s, f, i in zip(savings, fees, initials)]

cumulative = [net_flows[0]]
for i in range(1, roi_years):
    cumulative.append(cumulative[-1] + net_flows[i])

payback_year = compute_payback_year(net_flows)

fig = go.Figure()

fig.add_trace(go.Bar(x=x_years, y=[-v for v in initials], name="Initial Investment",
                     marker_color="grey", text=[f"-{currency_symbol}{int(v):,}" if v else "" for v in initials],
                     textposition="outside"))
fig.add_trace(go.Bar(x=x_years, y=savings, name="Annual Savings",
                     marker_color="green", text=[f"{currency_symbol}{int(v):,}" for v in savings],
                     textposition="outside"))
fig.add_trace(go.Bar(x=x_years, y=[-v for v in fees], name="SaaS Fee",
                     marker_color="red", text=[f"-{currency_symbol}{int(v):,}" if v else "" for v in fees],
                     textposition="outside"))
fig.add_trace(go.Scatter(x=x_years, y=cumulative, mode="lines+markers+text", name="Cumulative Net Savings",
                         line=dict(color="blue", width=3),
                         text=[f"{currency_symbol}{int(v):,}" for v in cumulative],
                         textposition="top center"))

if payback_year:
    fig.add_vline(x=payback_year, line_width=2, line_dash="dash", line_color="orange")
    fig.add_annotation(x=payback_year, y=max(cumulative) * 0.05,
                       text=f"Payback: Year {payback_year:.2f}",
                       showarrow=False, font=dict(color="orange", size=14), bgcolor="white")

fig.update_layout(
    barmode="relative",
    height=500,
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(color="black"),
    xaxis=dict(title="Year", tickmode="linear", dtick=1),
    yaxis=dict(title=f"Cash Flow ({currency_symbol})"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=20, r=20, t=30, b=30)
)

st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.subheader("📝 Notes")
st.markdown("""
- Savings and payback are indicative only based on current assumptions.
- Assumes BMS access and standard operating conditions.
- No additional hardware or engineering costs included.
""")
st.caption("Crafted by Univers AI • For Proposal Use Only • Powered by Streamlit")
