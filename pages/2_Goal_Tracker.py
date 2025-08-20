import streamlit as st, uuid, math
import base64
from datetime import date

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

st.title("Goal Tracker")

# Required session data
required_keys = ["FHI", "monthly_income", "monthly_expenses", "current_savings"]
if any(key not in st.session_state for key in required_keys):
    st.warning("⚠️ Please complete the homepage first.")
    st.stop()

# Initialize session state
if "goals" not in st.session_state:
    st.session_state.goals = {}
if "selected_goal" not in st.session_state:
    st.session_state.selected_goal = None

# Common emoji options
emoji_options = ["🎯", "💰", "🏠", "🚗", "🎓", "✈️", "💼", "❤️", "📚", "🛍️", "📈", "🎁"]

# Add new goal
if st.button("➕ Add New Goal"):
    goal_id = str(uuid.uuid4())
    st.session_state.goals[goal_id] = {
        "name": f"New Goal {len(st.session_state.goals)+1}",
        "goal_amount": 1000.0,
        "start_date": date.today(),
        "target_date": date.today(),
        "use_recommended_fhi": True,
        "emoji": "🎯",
        "progress": {}
    }
    st.session_state.selected_goal = goal_id
    st.rerun()

# Show list of goals
st.subheader("Your Goals")
goals = list(st.session_state.goals.items())
cols_per_row = 4
num_rows = math.ceil(len(goals) / cols_per_row)

for i in range(num_rows):
    row_goals = goals[i * cols_per_row:(i + 1) * cols_per_row]
    cols = st.columns(cols_per_row)
    for col, (goal_id, goal) in zip(cols, row_goals):
        with col:
            target_date = goal.get("target_date", date.today())
            start_date = goal.get("start_date", date.today())
            goal_amount = goal.get("goal_amount", 1000.0)
            current_savings = st.session_state.get("current_savings", 0)
            monthly_income = st.session_state.get("monthly_income", 0)
            monthly_expenses = st.session_state.get("monthly_expenses", 0)
            FHI = st.session_state.get("FHI", 0)
            min_fhi = FHI if goal.get("use_recommended_fhi", True) else 50

            delta = (target_date - start_date)
            months = max(delta.days // 30, 1)
            remaining_amount = max(goal_amount - current_savings, 0)
            required_monthly_saving = remaining_amount / months
            available_to_save = max(monthly_income - monthly_expenses, 0)
            on_track = required_monthly_saving <= available_to_save and FHI >= min_fhi

            with st.container(border=True):
                # Calculate saved amount based on months checked
                start_date = goal.get("start_date", date.today())
                target_date = goal.get("target_date", date.today())

                # Function to get all months between start and target
                def month_start(d: date) -> date:
                    return d.replace(day=1)

                def months_between(start: date, target: date):
                    m = month_start(start)
                    out = []
                    while m <= target:
                        out.append(m)
                        year = m.year + (m.month // 12)
                        month = (m.month % 12) + 1
                        m = m.replace(year=year, month=month, day=1)
                    return out

                months = months_between(start_date, target_date)
                total_months = len(months)
                goal_amount = goal.get("goal_amount", 1000.0)
                current_savings = st.session_state.get("current_savings", 0)

                # Base per month = evenly split goal - current savings
                base_pool = max(goal_amount - current_savings, 0.0)
                base_per_month = base_pool / total_months if total_months > 0 else 0.0

                # Count months marked as saved
                checked_months = [m for m in months if goal.get("progress", {}).get(m.strftime("%Y-%m"), False)]
                saved_amount = len(checked_months) * base_per_month

                # Progress as fraction
                progress = min(saved_amount / goal_amount, 1.0) if goal_amount > 0 else 0

                st.markdown(
                    f"""
                    <div style='text-align: left;'>
                        <div style='font-size: 2rem'>{goal.get('emoji', '🎯')}</div>
                        <div style='font-size: 1.2rem; font-weight: bold;'>{goal['name']}</div>
                        <div style='color: {'green' if progress >= 1.0 else 'orange'}; margin-bottom: 0.5rem;'>
                            {progress:.0%} of goal reached
                        </div>
                    </div>
                    """, unsafe_allow_html=True
                )
                st.progress(progress)

                if st.button("View", key=f"view_{goal_id}"):
                    st.session_state.selected_goal = goal_id
                    st.rerun()


# Show goal details
if st.session_state.selected_goal:
    goal_id = st.session_state.selected_goal
    goal = st.session_state.goals[goal_id]
    st.markdown("---")

    def month_start(d: date) -> date:
        return d.replace(day=1)

    def months_between(start: date, target: date):
        m = month_start(start)
        out = []
        while m <= target:
            out.append(m)
            year = m.year + (m.month // 12)
            month = (m.month % 12) + 1
            m = m.replace(year=year, month=month, day=1)
        return out

    # Roadmap tracker
    # Roadmap tracker
    with st.container(border=True):
        st.subheader("📆 Savings Roadmap")
        st.markdown(
            "Click a month to mark it as ✅ when you've set aside the required savings for that month. "
            "If you miss a month, the amount rolls over into the next one."
        )

        if "progress" not in goal:
            goal["progress"] = {}

        start_date = goal.get("start_date", date.today())
        target_date = goal.get("target_date", date.today())

        valid_schedule = True
        required_monthly_saving = 0.0

        if start_date >= target_date:
            st.warning("⚠️ Please set a Start Date earlier than the Target Date.")
            valid_schedule = False
        else:
            months = months_between(start_date, target_date)
            if not months:
                st.warning("⚠️ No months to show. Adjust your dates.")
                valid_schedule = False
            else:
                cols_per_row = 4  # 4 months per row
                for i, m in enumerate(months):
                    if i % cols_per_row == 0:
                        cols = st.columns(cols_per_row, gap="small")

                    with cols[i % cols_per_row]:
                        key = m.strftime("%Y-%m")
                        if key not in goal["progress"]:
                            goal["progress"][key] = False

                        # Single line checkbox with month and year
                        label = f"{m.strftime('%b %Y')}"
                        checked = st.checkbox(label, value=goal["progress"][key], key=f"chk_{goal_id}_{key}")
                        goal["progress"][key] = checked

                # --- Calculate required monthly saving ---
                total_months = len(months)
                base_pool = max(goal.get("goal_amount", 0.0) - st.session_state["current_savings"], 0.0)
                base_per_month = base_pool / total_months if total_months > 0 else 0.0

                checked_indices = [i for i, m in enumerate(months) if goal["progress"].get(m.strftime("%Y-%m"), False)]
                last_checked = max(checked_indices) if checked_indices else -1
                saved_amount = len(checked_indices) * base_per_month
                remaining_amount = max(base_pool - saved_amount, 0.0)

                future_months = months[last_checked + 1:] if last_checked >= 0 else months
                open_future_slots = [m for m in future_months if not goal["progress"].get(m.strftime("%Y-%m"), False)]

                required_monthly_saving = remaining_amount / len(open_future_slots) if open_future_slots else 0.0

                st.info(
                    f"💡 Required savings from now on: ₱{required_monthly_saving:,.2f} "
                    f"({len(open_future_slots)} month(s) remaining)."
                )



    # Goal settings
    with st.container(border=True):
        goal_name = st.text_input("✏️ Goal Name", value=goal["name"], key=f"goal_name_input_{goal_id}")
        st.session_state.goals[goal_id]["name"] = goal_name

        st.markdown("🌟 *Choose an Emoji Icon*")
        emoji_cols = st.columns(6)
        for i, icon in enumerate(emoji_options):
            if emoji_cols[i % 6].button(icon, key=f"emoji_{icon}_{goal_id}"):
                goal["emoji"] = icon
                st.rerun()

        col1, col2, col3 = st.columns(3)
        with col1:
            goal["goal_amount"] = st.number_input("💰 Target Amount (₱)", min_value=1000.0, step=1000.0,
                                                  format="%.2f", value=goal.get("goal_amount", 1000.0),
                                                  key=f"goal_amount_input_{goal_id}")
        with col2:
            goal["start_date"] = st.date_input("🚀 Start Date", value=goal.get("start_date", date.today()),
                                               key=f"start_date_input_{goal_id}")
        with col3:
            goal["target_date"] = st.date_input("📅 Target Date", min_value=goal["start_date"],
                                                value=goal.get("target_date", date.today()),
                                                key=f"target_date_input_{goal_id}")

        st.markdown("#### Financial Health Setting")
        goal["use_recommended_fhi"] = st.checkbox(
            f"Use your current FHI ({st.session_state.get('FHI', 0)})",
            value=goal.get("use_recommended_fhi", True),
            key=f"use_recommended_fhi_input_{goal_id}"
        )
        min_fhi = (st.session_state.get("FHI", 0) if goal["use_recommended_fhi"]
                   else st.slider("Set your own minimum FHI", 0, 100, int(st.session_state.get("FHI", 0)),
                                  key=f"min_fhi_slider_{goal_id}"))
        
        if st.button("🔍 Preview", key=f"preview_{goal_id}"):
            st.session_state.preview_trigger = True
        else:
            st.session_state.preview_trigger = False

    # Status check
    with st.container(border=True):
        st.subheader("Status Check")
        FHI = st.session_state["FHI"]
        monthly_income = st.session_state["monthly_income"]
        monthly_expenses = st.session_state["monthly_expenses"]
        current_savings = st.session_state["current_savings"]

        if not valid_schedule:
            st.warning("⚠️ Fix your dates above to see an accurate status check.")
        else:
            available_to_save = max(monthly_income - monthly_expenses, 0)
            if required_monthly_saving <= available_to_save and FHI >= min_fhi:
                st.success(f"✅ You're on track! Save ₱{required_monthly_saving:,.2f} per month.")
            else:
                st.error("🚨 You're not on track.")
                st.markdown(f"💡 Need to save: ₱{required_monthly_saving:,.2f}/month")
                st.markdown(f"⚠️ Can only save: ₱{available_to_save:,.2f}/month")

                # Suggestions section
                st.subheader("Suggestions 💡")
                if available_to_save <= 0:
                    st.warning("👉 Your expenses are equal to or greater than your income. Consider reducing expenses or increasing income sources.")
                elif required_monthly_saving > available_to_save:
                    st.info("👉 Try adjusting your goal: either increase your saving contributions, extend your target date, or lower your target amount.")
                if FHI < min_fhi:
                    st.warning("👉 Your Financial Health Index is too low. Focus on improving income-expense balance before setting aggressive savings goals.")
                if required_monthly_saving - available_to_save <= 1000:
                    st.success("👉 You're close! Small tweaks in spending could put you back on track.")

    if st.button("💾 Save Goal", key=f"save_goal_{goal_id}"):
        st.session_state.selected_goal = None
        st.rerun()
