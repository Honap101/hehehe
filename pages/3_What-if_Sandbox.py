import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import base64
from datetime import datetime

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

bg_base64 = get_base64_image("sidebar_background.png")  # Replace with your image path
logow_base64 = get_base64_image("logo_white.png") 
logoc_base64 = get_base64_image("logo_colored.png")

with st.sidebar:
    st.markdown(
        f"""
        <div style='
            display: flex;
            flex-direction: column;
            justify-content: flex-end;  /* push to bottom */
            align-items: center;
            text-align: center;
            padding: 0;
        '>
            <img src="data:image/png;base64,{logoc_base64}" 
                 width="150" 
                 style="display:block; margin-bottom:10px; filter: drop-shadow(2px 2px 5px white);">
            <h1 style='color:#ffffff; font-size:20px; margin:0;'>Fynstra AI</h1>
            <p style='color:#ffffff; font-size:14px; margin:0 0 20px 0;'>Your AI-Powered Financial Strategy and Analytics Platform</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- CSS for sidebar background with gradient overlay ---
st.markdown(
    f"""
    <style>
    [data-testid="stSidebar"] {{
        background: linear-gradient(to bottom, rgba(252,49,52,0.7), rgba(255,197,66,0.7)),
                    url("data:image/png;base64,{bg_base64}") no-repeat center;
        background-size: cover;
    }}

    /* Make all sidebar text white */
    [data-testid="stSidebar"] * {{
        color: white;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ===============================
# CALCULATION & HELPER FUNCTIONS
# ===============================

def calculate_fhi(age, monthly_income, monthly_expenses, monthly_savings, monthly_debt,
                  total_investments, net_worth, emergency_fund):
    """Calculate FHI score and components"""
    if age < 30:
        alpha, beta = 2.5, 2.0
    elif age < 40:
        alpha, beta = 3.0, 3.0
    elif age < 50:
        alpha, beta = 3.5, 4.0
    else:
        alpha, beta = 4.0, 5.0

    annual_income = monthly_income * 12

    Nworth = min(max((net_worth / (annual_income * alpha)) * 100, 0), 100) if annual_income > 0 else 0
    DTI = 100 - min((monthly_debt / monthly_income) * 100, 100) if monthly_income > 0 else 0
    Srate = min((monthly_savings / monthly_income) * 100, 100) if monthly_income > 0 else 0
    Invest = min(max((total_investments / (beta * annual_income)) * 100, 0), 100) if annual_income > 0 else 0
    Emerg = min((emergency_fund / monthly_expenses) / 6 * 100, 100) if monthly_expenses > 0 else 0

    FHI = 0.20 * Nworth + 0.15 * DTI + 0.15 * Srate + 0.15 * Invest + 0.20 * Emerg + 15

    components = {
        "Net Worth": Nworth,
        "Debt-to-Income": DTI,
        "Savings Rate": Srate,
        "Investment": Invest,
        "Emergency Fund": Emerg,
    }

    return FHI, components

def get_component_weights():
    """Return FHI component weights"""
    return {
        "Net Worth": 0.20,
        "Debt-to-Income": 0.15,
        "Savings Rate": 0.15,
        "Investment": 0.15,
        "Emergency Fund": 0.20,
        "_base": 15.0,
    }

def top_component_changes(old_components, new_components, k=2):
    """Identify the biggest movers for narrative explainability"""
    deltas = {k: round(new_components[k] - v, 1) for k, v in old_components.items()}
    sorted_up = sorted([x for x in deltas.items() if x[1] > 0], key=lambda x: -x[1])[:k]
    sorted_down = sorted([x for x in deltas.items() if x[1] < 0], key=lambda x: x[1])[:k]
    return sorted_up, sorted_down

def explain_fhi(components):
    """Return weighted contributions per component"""
    w = get_component_weights()
    contrib = {k: round(v * w[k], 2) for k, v in components.items()}
    total_weighted = round(sum(contrib.values()), 2)
    return contrib, total_weighted, w["_base"]

def create_comparison_chart(base_comp, new_comp):
    """Create a comparison chart for components"""
    try:
        categories = list(base_comp.keys())
        base_values = [float(v) if v is not None else 0.0 for v in base_comp.values()]
        new_values = [float(v) if v is not None else 0.0 for v in new_comp.values()]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=base_values,
            theta=categories,
            fill='toself',
            name='Current',
            line_color='blue',
            opacity=0.6
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=new_values,
            theta=categories,
            fill='toself',
            name='Scenario',
            line_color='red',
            opacity=0.6
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100])
            ),
            showlegend=True,
            height=400,
            title="Current vs Scenario Comparison"
        )
        
        return fig
    except Exception as e:
        # Fallback: simple bar chart if radar fails
        import plotly.express as px
        import pandas as pd
        
        df = pd.DataFrame({
            'Component': categories,
            'Current': base_values,
            'Scenario': new_values
        })
        
        fig = px.bar(df, x='Component', y=['Current', 'Scenario'], 
                     title="Current vs Scenario Comparison",
                     barmode='group')
        return fig

# ===============================
# MAIN APPLICATION
# ===============================

st.title("What-if Sandbox")
st.markdown("### 🧪 Test Financial Scenarios")

# Check if user has calculated FHI
required_keys = ["FHI", "monthly_income", "monthly_expenses", "current_savings"]
missing_keys = [key for key in required_keys if key not in st.session_state]

if missing_keys:
    st.warning("⚠️ Please complete the FHI calculation on the main Fynstra page first.")
    st.info("💡 This tool uses your current financial data to run 'what-if' scenarios.")
    st.info(f"Missing data: {', '.join(missing_keys)}")
    st.stop()

# Get current values from session state
current_age = st.session_state.get("age", 18)
current_income = st.session_state.get("monthly_income", 0.0)
current_expenses = st.session_state.get("monthly_expenses", 0.0)
current_savings = st.session_state.get("current_savings", 0.0)
current_debt = st.session_state.get("monthly_debt", 0.0)
current_investments = st.session_state.get("total_investments", 0.0)
current_networth = st.session_state.get("net_worth", 0.0)
current_emergency = st.session_state.get("emergency_fund", 0.0)
current_fhi = st.session_state.get("FHI", 0.0)

# Validate that we have meaningful data
if current_income <= 0 or current_expenses <= 0:
    st.error("❌ Invalid financial data detected. Please recalculate your FHI on the main page.")
    st.stop()

st.success(f"✅ Current FHI Score: **{current_fhi:.1f}/100**")

# ===============================
# SCENARIO PRESETS
# ===============================

with st.container(border=True):
    st.subheader("🚀 Quick Scenarios")
    st.caption("Click any scenario to instantly see the impact on your FHI score")
    
    col1, col2, col3, col4 = st.columns(4)
    
    preset = None
    
    with col1:
        if st.button("📉 Job Loss (2 months)", help="Model a 2-month period without income"):
            preset = {
                "name": "2-Month Job Loss",
                "income_pct": -100,
                "expenses_pct": 0,
                "savings_pct": -100,
                "debt_pct": 0,
                "invest_pct": 0,
                "efund_pct": 0
            }
    
    with col2:
        if st.button("📈 Salary Raise (+15%)", help="15% increase in monthly income"):
            preset = {
                "name": "15% Salary Raise",
                "income_pct": 15,
                "expenses_pct": 0,
                "savings_pct": 0,
                "debt_pct": 0,
                "invest_pct": 0,
                "efund_pct": 0
            }
    
    with col3:
        if st.button("💳 Debt Payoff", help="Pay off ₱5,000 additional debt monthly"):
            preset = {
                "name": "Extra Debt Payment",
                "income_pct": 0,
                "expenses_pct": 0,
                "savings_pct": 0,
                "debt_abs_delta": -5000,
                "invest_pct": 0,
                "efund_pct": 0
            }
    
    with col4:
        if st.button("🏦 Start Investing", help="Begin investing ₱3,000 monthly"):
            preset = {
                "name": "Start Investment Plan",
                "income_pct": 0,
                "expenses_pct": 0,
                "savings_abs_delta": 3000,
                "debt_pct": 0,
                "invest_pct": 20,
                "efund_pct": 0
            }

# ===============================
# CUSTOM SCENARIO BUILDER
# ===============================

with st.container(border=True):
    st.subheader("🎛️ Custom Scenario Builder")
    st.caption("Adjust any financial parameter to see how it affects your FHI score")
    
    # Apply preset values if selected
    if preset:
        st.info(f"📋 Applied preset: **{preset['name']}**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Income & Expenses**")
        income_pct = st.slider(
            "Income Change (%)", 
            -50, 50, 
            preset.get("income_pct", 0) if preset else 0, 
            step=1,
            help="Percentage change in monthly income"
        )
        expenses_pct = st.slider(
            "Expenses Change (%)", 
            -30, 30, 
            preset.get("expenses_pct", 0) if preset else 0, 
            step=1,
            help="Percentage change in monthly expenses"
        )
    
    with col2:
        st.markdown("**Savings & Debt**")
        savings_pct = st.slider(
            "Savings Change (%)", 
            -50, 50, 
            preset.get("savings_pct", 0) if preset else 0, 
            step=1,
            help="Percentage change in monthly savings"
        )
        debt_pct = st.slider(
            "Debt Payments Change (%)", 
            -30, 50, 
            preset.get("debt_pct", 0) if preset else 0, 
            step=1,
            help="Percentage change in monthly debt payments"
        )
    
    with col3:
        st.markdown("**Investments & Emergency Fund**")
        invest_pct = st.slider(
            "Investment Growth (%)", 
            -30, 50, 
            preset.get("invest_pct", 0) if preset else 0, 
            step=1,
            help="Percentage change in total investments"
        )
        efund_pct = st.slider(
            "Emergency Fund Change (%)", 
            -30, 50, 
            preset.get("efund_pct", 0) if preset else 0, 
            step=1,
            help="Percentage change in emergency fund"
        )
    
    # Handle absolute deltas from presets
    debt_abs_delta = preset.get("debt_abs_delta", 0) if preset else 0
    savings_abs_delta = preset.get("savings_abs_delta", 0) if preset else 0

# ===============================
# SCENARIO CALCULATION
# ===============================

# Calculate scenario values
scenario_income = max(0.0, current_income * (1 + income_pct/100))
scenario_expenses = max(0.0, current_expenses * (1 + expenses_pct/100))
scenario_savings = max(0.0, current_savings * (1 + savings_pct/100) + savings_abs_delta)
scenario_debt = max(0.0, current_debt * (1 + debt_pct/100) + debt_abs_delta)
scenario_investments = max(0.0, current_investments * (1 + invest_pct/100))
scenario_emergency = max(0.0, current_emergency * (1 + efund_pct/100))

# Calculate new FHI
new_fhi, new_components = calculate_fhi(
    current_age, scenario_income, scenario_expenses, scenario_savings,
    scenario_debt, scenario_investments, current_networth, scenario_emergency
)

# Get current components for comparison
current_fhi_calc, current_components = calculate_fhi(
    current_age, current_income, current_expenses, current_savings,
    current_debt, current_investments, current_networth, current_emergency
)

# ===============================
# RESULTS DISPLAY
# ===============================

st.markdown("---")
st.subheader("📊 Scenario Results")

# Main metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Current FHI", 
        f"{current_fhi:.1f}",
        help="Your actual FHI score from the calculator"
    )

with col2:
    fhi_change = new_fhi - current_fhi
    st.metric(
        "Scenario FHI", 
        f"{new_fhi:.1f}", 
        delta=f"{fhi_change:+.1f}",
        help="Your FHI score under this scenario"
    )

with col3:
    # Impact assessment
    if abs(fhi_change) < 1:
        impact = "Minimal Impact"
        impact_color = "gray"
    elif abs(fhi_change) < 5:
        impact = "Low Impact"
        impact_color = "blue"
    elif abs(fhi_change) < 10:
        impact = "Moderate Impact"
        impact_color = "orange"
    else:
        impact = "High Impact"
        impact_color = "red" if fhi_change < 0 else "green"
    
    st.metric(
        "Impact Level",
        impact,
        help="Overall impact of this scenario on your financial health"
    )

# Scenario summary table
with st.container(border=True):
    st.markdown("**Scenario Summary**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Current → Scenario**")
        changes_data = {
            "Parameter": ["Monthly Income", "Monthly Expenses", "Monthly Savings", "Monthly Debt", "Total Investments", "Emergency Fund"],
            "Current": [f"₱{current_income:,.0f}", f"₱{current_expenses:,.0f}", f"₱{current_savings:,.0f}", 
                       f"₱{current_debt:,.0f}", f"₱{current_investments:,.0f}", f"₱{current_emergency:,.0f}"],
            "Scenario": [f"₱{scenario_income:,.0f}", f"₱{scenario_expenses:,.0f}", f"₱{scenario_savings:,.0f}",
                        f"₱{scenario_debt:,.0f}", f"₱{scenario_investments:,.0f}", f"₱{scenario_emergency:,.0f}"],
            "Change": [f"{income_pct:+}%", f"{expenses_pct:+}%", f"{savings_pct:+}%" + (f" +₱{savings_abs_delta:,.0f}" if savings_abs_delta else ""),
                      f"{debt_pct:+}%" + (f" ₱{debt_abs_delta:,.0f}" if debt_abs_delta else ""), 
                      f"{invest_pct:+}%", f"{efund_pct:+}%"]
        }
        
        st.dataframe(changes_data, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("**Component Score Changes**")
        component_data = []
        for component in current_components.keys():
            current_score = current_components[component]
            new_score = new_components[component]
            change = new_score - current_score
            
            component_data.append({
                "Component": component,
                "Current": f"{current_score:.1f}",
                "Scenario": f"{new_score:.1f}",
                "Δ": f"{change:+.1f}"
            })
        
        st.dataframe(component_data, use_container_width=True, hide_index=True)

# Visualization
col1, col2 = st.columns(2)

with col1:
    # Radar chart comparison
    st.plotly_chart(
        create_comparison_chart(current_components, new_components), 
        use_container_width=True
    )

with col2:
    # Key insights
    st.markdown("**📈 Key Insights**")
    
    # Biggest movers
    improvements, declines = top_component_changes(current_components, new_components, k=2)
    
    if improvements:
        st.success("**Improvements:**")
        for component, change in improvements:
            st.write(f"• {component}: +{change:.1f} points")
    
    if declines:
        st.error("**Declines:**")
        for component, change in declines:
            st.write(f"• {component}: {change:.1f} points")
    
    if not improvements and not declines:
        st.info("No significant changes in component scores.")
    
    # Overall assessment
    if fhi_change > 5:
        st.success(f"🎯 This scenario would significantly improve your financial health by {fhi_change:.1f} points!")
    elif fhi_change > 0:
        st.info(f"👍 This scenario would improve your FHI by {fhi_change:.1f} points.")
    elif fhi_change > -5:
        st.warning(f"⚠️ This scenario would slightly decrease your FHI by {abs(fhi_change):.1f} points.")
    else:
        st.error(f"🚨 This scenario would significantly impact your financial health (-{abs(fhi_change):.1f} points).")

# ===============================
# EXPLAINABILITY SECTION
# ===============================

with st.expander("🧠 How FHI is Calculated (Explainability)", expanded=False):
    st.caption("Understanding how the Financial Health Index score is computed")
    
    # Formula
    st.latex(r"""
        \textbf{FHI} = 0.20 \times NW + 0.15 \times DTI + 0.15 \times SR + 0.15 \times INV + 0.20 \times EF + 15
    """)
    
    w = get_component_weights()
    st.markdown(f"""
    **Component Weights:**
    - Net Worth: {int(w['Net Worth']*100)}%
    - Debt-to-Income: {int(w['Debt-to-Income']*100)}%  
    - Savings Rate: {int(w['Savings Rate']*100)}%
    - Investment: {int(w['Investment']*100)}%
    - Emergency Fund: {int(w['Emergency Fund']*100)}%
    - Base Score: {w['_base']} points
    """)
    
    # Detailed breakdown
    current_contrib, current_weighted, base_const = explain_fhi(current_components)
    scenario_contrib, scenario_weighted, _ = explain_fhi(new_components)
    
    st.markdown("**Weighted Contribution Breakdown:**")
    breakdown_data = []
    for component in current_components.keys():
        breakdown_data.append({
            "Component": component,
            "Current Contribution": f"{current_contrib[component]:.2f}",
            "Scenario Contribution": f"{scenario_contrib[component]:.2f}",
            "Change": f"{scenario_contrib[component] - current_contrib[component]:+.2f}"
        })
    
    breakdown_data.append({
        "Component": "Base Score",
        "Current Contribution": f"{base_const:.2f}",
        "Scenario Contribution": f"{base_const:.2f}",
        "Change": "0.00"
    })
    
    st.dataframe(breakdown_data, use_container_width=True, hide_index=True)

# ===============================
# ACTION RECOMMENDATIONS
# ===============================

if fhi_change != 0:
    with st.container(border=True):
        st.subheader("💡 Actionable Recommendations")
        
        if fhi_change > 0:
            st.success("This scenario shows positive potential! Here's how to implement it:")
            
            if income_pct > 0:
                st.write(f"📈 **Increase Income by {income_pct}%**: Consider skill development, side hustles, or salary negotiations")
            
            if expenses_pct < 0:
                st.write(f"📉 **Reduce Expenses by {abs(expenses_pct)}%**: Review subscriptions, optimize spending, find better deals")
            
            if savings_pct > 0 or savings_abs_delta > 0:
                st.write(f"💰 **Boost Savings**: Automate transfers, use high-yield accounts")
            
            if debt_abs_delta < 0:
                st.write(f"💳 **Accelerate Debt Payment**: Consider debt avalanche or snowball methods")
            
            if invest_pct > 0:
                st.write(f"📊 **Increase Investments**: Explore index funds, MP2, or other diversified options")
                
        else:
            st.warning("This scenario shows potential challenges. Consider these protective measures:")
            
            if income_pct < 0:
                st.write("🛡️ **Income Protection**: Build emergency fund, develop multiple income streams")
            
            if expenses_pct > 0:
                st.write("⚠️ **Expense Management**: Create strict budget, identify cost-cutting opportunities")

# Save scenario functionality
if st.button("💾 Save This Scenario", key="save_scenario"):
    if "saved_scenarios" not in st.session_state:
        st.session_state.saved_scenarios = []
    
    scenario_data = {
        "name": preset.get("name", "Custom Scenario") if preset else "Custom Scenario",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "current_fhi": current_fhi,
        "scenario_fhi": new_fhi,
        "change": fhi_change,
        "parameters": {
            "income_pct": income_pct,
            "expenses_pct": expenses_pct,
            "savings_pct": savings_pct,
            "debt_pct": debt_pct,
            "invest_pct": invest_pct,
            "efund_pct": efund_pct
        }
    }
    
    st.session_state.saved_scenarios.append(scenario_data)
    st.success("✅ Scenario saved! You can review saved scenarios below.")

# Display saved scenarios
if st.session_state.get("saved_scenarios"):
    with st.expander("📁 Saved Scenarios", expanded=False):
        for i, scenario in enumerate(st.session_state.saved_scenarios):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{scenario['name']}**")
                st.caption(f"Saved: {scenario['timestamp']}")
            
            with col2:
                change_color = "green" if scenario['change'] > 0 else "red"
                st.markdown(f"FHI: {scenario['scenario_fhi']:.1f} (<span style='color:{change_color}'>{scenario['change']:+.1f}</span>)", unsafe_allow_html=True)
            
            with col3:
                if st.button("🗑️ Delete", key=f"delete_scenario_{i}"):
                    st.session_state.saved_scenarios.pop(i)
                    st.rerun()

st.markdown("---")
st.caption("💡 **Tip**: Use this tool regularly to test different financial strategies and see their potential impact before making real changes to your finances.")
