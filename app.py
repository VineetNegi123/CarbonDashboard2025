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

st.set_page_config(page_title="CO₂ & ROI Dashboard", layout="wide")

st.markdown("""
    <style>
        body {
            background-color: #f5f5f5;
            color: #1a1a1a;
        }
        .block-container {
            padding: 1rem 2rem;
            background-color: #f5f5f5;
        }
        h1, h2, h3, h4, h5, h6, p {
            color: #1a1a1a;
        }
    </style>
""", unsafe_allow_html=True)

currency_options = {"USD": "$", "SGD": "S$", "MYR": "RM", "IDR": "Rp", "HKD": "HK$", "RMB": "¥"}
st.sidebar.markdown("### Currency")
selected_currency = st.sidebar.selectbox("Select Currency", list(currency_options.keys()), index=1)
currency_symbol = f"{currency_options[selected_currency]}"

country_factors = {
    "Indonesia": 0.87, "Singapore": 0.408, "Malaysia": 0.585, "Thailand": 0.513,
    "Vietnam": 0.618, "Philippines": 0.65, "China": 0.555, "Japan": 0.474,
    "South Korea": 0.405, "India": 0.82, "Australia": 0.79, "United States": 0.42,
    "United Kingdom": 0.233, "Germany": 0.338, "Custom": None
}

st.header("Input Parameters")
col1, col2, col3 = st.columns(3)

with col1:
    energy_savings = st.number_input("Estimated Energy Savings (kWh/year)", value=1040249.0)
    electricity_rate = st.number_input(f"Electricity Rate ({currency_symbol}/kWh)", value=0.14)
    cooling_energy = st.number_input("Cooling Energy (RTh/year)", value=21900000.00, format="%.2f")

with col2:
    selected_country = st.selectbox("Select Country", list(country_factors.keys()))
    carbon_emission_factor = st.number_input("Custom CO₂ Factor (kg/kWh)", value=0.82) \
        if selected_country == "Custom" else country_factors[selected_country]
    roi_years = st.selectbox("ROI Duration (Years)", options=[3, 5])
    efficiency_pct = st.number_input("Efficiency Improvement (%)", value=5.0, format="%.2f") / 100

with col3:
    initial_investment = st.number_input(f"Initial Investment ({currency_symbol})", value=88817.0)
    one_time_install = st.number_input(f"One-Time Installation ({currency_symbol})", value=16000.0)
    software_fee = st.number_input(f"Annual SaaS Fee ({currency_symbol})", value=72817.0)

carbon_reduction = energy_savings * carbon_emission_factor
annual_savings = energy_savings * electricity_rate
payback_text = f"{initial_investment / annual_savings:.2f} yrs" if annual_savings > 0 else "Not achievable"

# ------------------------- Corrected ROI Waterfall Chart -------------------------- #
measures = ["absolute", "relative"] + ["relative"] * roi_years + ["total"]
labels = ["Start", "Investment"] + [f"Year {i+1} Savings" for i in range(roi_years)] + ["Net Benefit"]
values = [0, -initial_investment]

for i in range(roi_years):
    yearly_value = annual_savings - (software_fee if i >= 1 else 0)
    values.append(yearly_value)

net_benefit = sum(values[2:])
values.append(net_benefit)

fig = go.Figure(go.Waterfall(
    name="ROI",
    orientation="v",
    measure=measures,
    x=labels,
    text=[f"{currency_symbol}{v:,.0f}" for v in values],
    textposition="outside",
    y=values,
    connector={"line": {"color": "#888"}},
    increasing={"marker": {"color": "#60d394"}},
    decreasing={"marker": {"color": "#fc6471"}},
    totals={"marker": {"color": "#4aa7f9"}}
))

fig.update_layout(
    height=500,
    margin=dict(t=40, l=20, r=20, b=40),
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
    font=dict(size=14, color="#1a1a1a"),
    title="5-Year ROI Forecast",
    yaxis_title=f"Cash Flow ({currency_symbol})"
)

# ---------------------- Summary Boxes with Descriptions --------------------------- #
st.subheader("Summary Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div style='background-color:#f0f2f5; padding:20px; border-radius:10px; color:#1a1a1a;'>
        <h4> Initial Investment</h4>
        <h2 style='color:#1a1a1a;'>{currency_symbol}{int(initial_investment):,}</h2>
        <p style='font-size:13px;'>One-time setup including hardware, software, and installation</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='background-color:#f0f2f5; padding:20px; border-radius:10px; color:#1a1a1a;'>
        <h4> Annual Energy Savings</h4>
        <h2 style='color:#1a1a1a;'>{currency_symbol}{int(annual_savings):,}</h2>
        <p style='font-size:13px;'>Recurring yearly savings from optimized HVAC operations</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style='background-color:#f0f2f5; padding:20px; border-radius:10px; color:#1a1a1a;'>
        <h4> Payback Period</h4>
        <h2 style='color:#1a1a1a;'>{payback_text}</h2>
        <p style='font-size:13px;'>Time to recover initial investment through savings</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    roi_percent = (net_benefit / initial_investment) * 100
    st.markdown(f"""
    <div style='background-color:#f0f2f5; padding:20px; border-radius:10px; color:#1a1a1a;'>
        <h4> {roi_years}-Year ROI</h4>
        <h2 style='color:#1a1a1a;'>{roi_percent:.0f}%</h2>
        <p style='font-size:13px;'>Return on investment over the analysis period</p>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div style='background-color:#f0f2f5; padding:20px; border-radius:10px; color:#1a1a1a;'>
        <h4> Carbon Reduction</h4>
        <h2 style='color:#007acc;'>{carbon_reduction/1000:.1f} tCO₂e/year</h2>
        <p style='font-size:13px;'>Estimated annual CO₂ emissions reduction</p>
    </div>
    """, unsafe_allow_html=True)

st.plotly_chart(fig, use_container_width=True)

# ------------------- Footer Banner ---------------------- #
st.markdown(f"""
<div style='background: linear-gradient(90deg, #fd7e14, #f94f4f); padding: 30px; border-radius: 12px; margin-top: 30px; text-align: center;'>
    <h2 style='color: white; margin-bottom: 0;'>Total Net Benefit</h2>
    <h1 style='color: white; font-size: 48px; margin-top: 5px;'>{currency_symbol}{int(net_benefit):,}</h1>
    <p style='color: white; font-size: 14px;'>Cumulative savings after recovering initial investment over {roi_years} years</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
---
### Notes
- Savings are indicative only and assume 12 months of clean interval energy + HVAC data; we will recalculate once verified data is available.  
- We assume your BMS offers read/write API access with documented point names and units; exact scope and timeline will be set after we review the point list.  
- Models use current schedules, set-points and occupancy; any major change (new tenants, longer hours, etc.) will shift both baseline and savings.  
- Cost and CO₂ figures use prevailing market values.  
- No new meters, controllers, network upgrades or cybersecurity work are included; any required additions will be separately scoped and priced after a joint site survey.
""")

st.caption("Crafted by Univers AI • For Proposal Use Only • Powered by Streamlit")
