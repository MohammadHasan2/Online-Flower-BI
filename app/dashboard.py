import hmac
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from etl.run_pipeline import main as run_etl
from database.connection import engine
from datetime import date, timedelta
import pandas as pd

from queries import (
    get_orders_by_status,
    get_recent_orders,
    get_revenue_over_time,
    get_top_products,
    get_total_revenue,
    get_total_orders,
    get_total_customers,
    get_products_sold,
    get_last_etl_run,
    get_all_customers,
    search_customer_by_phone,
)


# ============================================================
# PAGE CONFIG
# ============================================================


st.set_page_config(
    page_title="Flower Shop Analytics",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# PASSWORD PROTECTION
# ============================================================

def check_password():

    if st.session_state.get("authenticated", False):
        return True

    st.markdown(
    """
    <style>

                div.stButton > button {
            background: linear-gradient(
                135deg,
                #8E5AA8,
                #684080
            ) !important;

            color: white !important;

            border: none !important;

            border-radius: 12px !important;

            font-weight: 750 !important;

            min-height: 44px;

            box-shadow:
                0 8px 18px rgba(104, 64, 128, 0.20);

            transition: all 0.2s ease;
        }

        div.stButton > button:hover {
            background: linear-gradient(
                135deg,
                #9B6BB0,
                #71478A
            ) !important;

            color: white !important;

            transform: translateY(-1px);

            box-shadow:
                0 11px 24px rgba(104, 64, 128, 0.28);
        }

        div.stButton > button:active {
            transform: translateY(0);
        }
    
        .login-box {
            max-width: 500px;
            margin: 120px auto 20px auto;
            text-align: center;
        }

        .login-title {
            font-size: 2rem;
            font-weight: 800;
            color: #4B2E5A;
            margin-bottom: 6px;
            letter-spacing: -0.03em;
        }

        .login-subtitle {
            color: #76677F;
            font-size: 0.95rem;
            margin-bottom: 25px;
        }

        .login-icon {
            width: 68px;
            height: 68px;
            margin: 0 auto 20px auto;
            border-radius: 20px;

            display: flex;
            align-items: center;
            justify-content: center;

            background: linear-gradient(
                135deg,
                #8E5AA8,
                #684080
            );

            color: white;
            font-size: 30px;

            box-shadow:
                0 12px 30px rgba(104, 64, 128, 0.22);
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="login-box"></div>',
        unsafe_allow_html=True,
    )

    st.title("🌸Flower Shop Analytics")

    st.caption(
        "Enter your password to access the analytics dashboard."
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password",
    )

    if st.button(
        "Sign In",
        type="primary",
        use_container_width=True,
    ):

        expected_password = st.secrets["APP_PASSWORD"]

        if hmac.compare_digest(
            password,
            expected_password,
        ):
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")

    return False

# ============================================================
# REQUIRE LOGIN
# ============================================================

if not check_password():
    st.stop()


# ============================================================
# PROFESSIONAL UI / THEME
# ============================================================

st.markdown(
    """
    <style>
        /* ---------- Global ---------- */
        :root {
            --ink: #172033;
            --muted: #6b7280;
            --soft: #f7f8fb;
            --border: #e7e9ef;
            --card: #ffffff;
            --accent: #9b4d68;
            --accent-dark: #7d3c53;
            --accent-soft: #f7edf1;
            --green: #267a57;
            --green-soft: #edf8f2;
            --red: #b54747;
            --red-soft: #fff1f1;
            --gold: #a8792e;
        }

        .stApp {
            background:
                radial-gradient(circle at 88% 0%, rgba(155, 77, 104, 0.045), transparent 24%),
                #fbfbfc;
            color: var(--ink);
        }

        .block-container {
            max-width: 1480px;
            padding-top: 2.0rem;
            padding-bottom: 4rem;
            padding-left: 3rem;
            padding-right: 3rem;
        }

        /* Hide Streamlit chrome that doesn't add value to the dashboard */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }

        /* ---------- Sidebar ---------- */
        [data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid var(--border);
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.4rem;
        }

        [data-testid="stSidebar"] .stMarkdown {
            color: var(--ink);
        }

        [data-testid="stSidebar"] hr {
            border-color: var(--border);
            margin: 1.2rem 0;
        }

        /* ---------- Typography ---------- */
        h1, h2, h3, h4 {
            color: var(--ink) !important;
            letter-spacing: -0.025em;
        }

        h1 {
            font-size: 2.25rem !important;
            font-weight: 750 !important;
        }

        h2 {
            font-size: 1.35rem !important;
            font-weight: 700 !important;
        }

        h3 {
            font-size: 1.08rem !important;
            font-weight: 700 !important;
        }

        p, label, .stCaption {
            color: var(--muted);
        }

        /* ---------- Brand header ---------- */
        .brand-row {
            display: flex;
            align-items: center;
            gap: 14px;
            margin-bottom: 4px;
        }

        .brand-mark {
            width: 48px;
            height: 48px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(145deg, #a85b77, #7d3c53);
            color: white;
            font-size: 23px;
            box-shadow: 0 10px 25px rgba(125, 60, 83, 0.18);
        }

        .brand-title {
            font-size: 2rem;
            line-height: 1.05;
            font-weight: 780;
            color: var(--ink);
            letter-spacing: -0.04em;
        }

        .brand-subtitle {
            margin-top: 5px;
            color: var(--muted);
            font-size: 0.96rem;
        }

        .page-kicker {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            margin-top: 22px;
            margin-bottom: 8px;
            color: var(--accent-dark);
            font-size: 0.76rem;
            font-weight: 800;
            letter-spacing: 0.11em;
            text-transform: uppercase;
        }

        /* ---------- Cards ---------- */
        .metric-card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 18px 20px;
            min-height: 128px;
            box-shadow: 0 5px 18px rgba(23, 32, 51, 0.035);
            position: relative;
            overflow: hidden;
        }

        .metric-card::after {
            content: "";
            position: absolute;
            right: -24px;
            top: -28px;
            width: 92px;
            height: 92px;
            border-radius: 50%;
            background: var(--accent-soft);
        }

        .metric-label {
            position: relative;
            z-index: 1;
            color: var(--muted);
            font-size: 0.80rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        .metric-value {
            position: relative;
            z-index: 1;
            margin-top: 10px;
            color: var(--ink);
            font-size: 1.78rem;
            line-height: 1.1;
            font-weight: 780;
            letter-spacing: -0.035em;
        }

        .metric-icon {
            position: absolute;
            z-index: 2;
            right: 18px;
            top: 17px;
            font-size: 20px;
        }

        .panel {
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 5px 18px rgba(23, 32, 51, 0.03);
        }

        .panel-title {
            color: var(--ink);
            font-size: 1.05rem;
            font-weight: 750;
            margin-bottom: 2px;
        }

        .panel-caption {
            color: var(--muted);
            font-size: 0.82rem;
            margin-bottom: 14px;
        }

        /* ---------- ETL status ---------- */
        .pipeline-card {
            border: 1px solid var(--border);
            background: #ffffff;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 5px 18px rgba(23, 32, 51, 0.03);
        }

        .pipeline-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
        }

        .pipeline-icon {
            width: 36px;
            height: 36px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--accent-soft);
            font-size: 17px;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            padding: 7px 11px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 750;
        }

        .status-success {
            color: var(--green);
            background: var(--green-soft);
        }

        .status-failed {
            color: var(--red);
            background: var(--red-soft);
        }

        .status-running {
            color: var(--gold);
            background: #fff8e8;
        }

        .pipeline-stat-label {
            color: var(--muted);
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }

        .pipeline-stat-value {
            color: var(--ink);
            font-size: 0.92rem;
            font-weight: 650;
            margin-top: 4px;
        }

        /* ---------- Buttons ---------- */
        .stButton > button {
            border-radius: 10px;
            font-weight: 700;
            min-height: 42px;
            border: 1px solid var(--border);
            transition: all 0.18s ease;
        }

        .stButton > button:hover {
            border-color: #c9a5b3;
            transform: translateY(-1px);
            box-shadow: 0 7px 18px rgba(23, 32, 51, 0.08);
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #9b4d68, #7d3c53);
            border-color: #7d3c53;
            color: white;
        }

        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #a85b77, #7d3c53);
            border-color: #7d3c53;
        }

        /* ---------- Inputs ---------- */
        .stSelectbox > div > div,
        .stTextInput > div > div {
            border-radius: 10px;
            border-color: var(--border);
        }

        /* ---------- Tables ---------- */
        [data-testid="stDataFrame"] {
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
        }

        /* ---------- Alerts ---------- */
        [data-testid="stAlert"] {
            border-radius: 12px;
        }

        /* ---------- Divider ---------- */
        hr {
            border-color: var(--border);
            margin: 1.6rem 0;
        }

        /* ---------- Sync area ---------- */
        .sync-description {
            display: flex;
            align-items: center;
            height: 42px;
            padding-left: 3px;
            color: var(--muted);
            font-size: 0.84rem;
        }

        /* ---------- Mobile ---------- */
        @media (max-width: 900px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .brand-title {
                font-size: 1.65rem;
            }

            h1 {
                font-size: 1.8rem !important;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="brand-row">
        <div class="brand-mark">🌸</div>
        <div>
            <div class="brand-title">Flower Shop Analytics</div>
            <div class="brand-subtitle">
                A clear view of sales, customers, products, and operations.
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    """
    <div style="
        display:flex;
        align-items:center;
        gap:10px;
        margin-bottom:20px;
    ">
        <div style="
            width:36px;
            height:36px;
            border-radius:10px;
            display:flex;
            align-items:center;
            justify-content:center;
            background:#f7edf1;
            font-size:18px;
        ">🌸</div>
        <div>
            <div style="font-weight:800;color:#172033;font-size:0.98rem;">
                Flower Shop
            </div>
            <div style="color:#8a909c;font-size:0.72rem;">
                Analytics workspace
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown(
    '<div style="font-size:0.72rem;font-weight:800;letter-spacing:.1em;'
    'text-transform:uppercase;color:#8a909c;margin-bottom:8px;">Analytics</div>',
    unsafe_allow_html=True,
)

st.sidebar.caption("Choose the period you want to analyze.")

today = date.today()

date_option = st.sidebar.selectbox(
    "Date range",
    [
        "Today",
        "Last 7 days",
        "Last 30 days",
        "This month",
        "All time",
    ],
)

if date_option == "Today":
    start_date = today
    end_date = today

elif date_option == "Last 7 days":
    start_date = today - timedelta(days=6)
    end_date = today

elif date_option == "Last 30 days":
    start_date = today - timedelta(days=29)
    end_date = today

elif date_option == "This month":
    start_date = today.replace(day=1)
    end_date = today

else:
    start_date = None
    end_date = None

st.sidebar.divider()

customer_page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "👥 Customers",
    ],
)

st.sidebar.divider()

st.sidebar.markdown(
    """
    <div style="
        padding:13px;
        border:1px solid #e7e9ef;
        border-radius:12px;
        background:#fafbfc;
    ">
        <div style="font-size:.72rem;color:#8a909c;font-weight:750;
                    text-transform:uppercase;letter-spacing:.06em;">
            Data sources
        </div>
        <div style="font-size:.8rem;color:#4b5563;margin-top:8px;">
            <div>◦ Google Sheets</div>
            <div style="margin-top:4px;">◦ Supabase PostgreSQL</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SYNC SECTION
# ============================================================

sync_col, status_col = st.columns([1, 3], vertical_alignment="center")

with sync_col:
    sync_clicked = st.button(
        "↻  Sync Latest Data",
        type="primary",
        use_container_width=True,
    )

with status_col:
    st.markdown(
        '<div class="sync-description">'
        'Synchronize the latest orders from Google Sheets with the analytics database.'
        '</div>',
        unsafe_allow_html=True,
    )

if sync_clicked:
    with st.spinner("Running ETL pipeline..."):
        try:
            result = run_etl()

            st.success("Data synchronized successfully.")
            st.info(f"Rows processed: {result['rows_processed']}")

            st.rerun()

        except Exception as error:
            st.error(f"ETL failed: {error}")


# ============================================================
# CUSTOMERS PAGE
# ============================================================

if customer_page == "👥 Customers":

    st.markdown(
        '<div class="page-kicker">CUSTOMER DIRECTORY</div>',
        unsafe_allow_html=True,
    )
    st.title("Customers")
    st.caption("View registered customers and quickly search by phone number.")

    with engine.connect() as connection:
        customers_data = get_all_customers(connection)

    st.markdown(
        '<div class="panel-title" style="margin-top:22px;">All Customers</div>',
        unsafe_allow_html=True,
    )
    st.caption("Registered customers currently available in the database.")

    if customers_data:
        customers_df = pd.DataFrame(
            customers_data,
            columns=[
                "ID",
                "Name",
                "Phone",
            ],
        )

        st.dataframe(
            customers_df[
                [
                    "Name",
                    "Phone",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("No customers found.")

    st.divider()

    st.markdown(
        '<div class="panel-title">Search Customer</div>',
        unsafe_allow_html=True,
    )
    st.caption("Find a customer using their registered phone number.")

    phone = st.text_input(
        "Enter customer phone number",
        placeholder="e.g. 03xxxxxx",
    )

    if st.button(
        "Search Customer",
        type="primary",
    ):
        if not phone.strip():
            st.warning("Please enter a phone number.")

        else:
            with engine.connect() as connection:
                customer = search_customer_by_phone(
                    connection,
                    phone.strip(),
                )

            if customer:
                st.success("Customer found.")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Name",
                        customer.name,
                    )

                with col2:
                    st.metric(
                        "Phone",
                        customer.phone,
                    )

            else:
                st.error("Customer not found.")


# ============================================================
# DASHBOARD
# ============================================================

elif customer_page == "📊 Dashboard":

    # --------------------------------------------------------
    # DATABASE QUERIES
    # --------------------------------------------------------

    with engine.connect() as connection:

        revenue = get_total_revenue(
            connection,
            start_date,
            end_date,
        )

        orders = get_total_orders(
            connection,
            start_date,
            end_date,
        )

        customers = get_total_customers(
            connection,
        )

        products_sold = get_products_sold(
            connection,
            start_date,
            end_date,
        )

        last_run = get_last_etl_run(
            connection,
        )

        revenue_data = get_revenue_over_time(
            connection,
            start_date,
            end_date,
        )

        top_products = get_top_products(
            connection,
            start_date,
            end_date,
        )

        status_data = get_orders_by_status(
            connection,
            start_date,
            end_date,
        )

        recent_orders = get_recent_orders(
            connection,
            start_date,
            end_date,
        )

    # --------------------------------------------------------
    # DASHBOARD CONTEXT
    # --------------------------------------------------------

    period_label = {
        "Today": "Today",
        "Last 7 days": "Last 7 days",
        "Last 30 days": "Last 30 days",
        "This month": "This month",
        "All time": "All time",
    }[date_option]

    st.markdown(
        f'<div class="page-kicker">BUSINESS OVERVIEW · {period_label.upper()}</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    metric_cols = st.columns(4)

    metrics = [
        ("Revenue", f"${revenue:,.2f}", "💰"),
        ("Orders", f"{orders:,}", "🛒"),
        ("Customers", f"{customers:,}", "👥"),
        ("Products Sold", f"{products_sold:,}", "🌸"),
    ]

    for col, (label, value, icon) in zip(metric_cols, metrics):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-icon">{icon}</div>
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # --------------------------------------------------------
    # REVENUE + ORDER STATUS
    # --------------------------------------------------------

    st.divider()

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown(
            """
            <div class="panel-title">Revenue Trend</div>
            <div class="panel-caption">
                Revenue generated across the selected period.
            </div>
            """,
            unsafe_allow_html=True,
        )

        if revenue_data:
            revenue_df = pd.DataFrame(
                revenue_data,
                columns=[
                    "date",
                    "revenue",
                ],
            )

            revenue_df["revenue"] = revenue_df["revenue"].astype(float)

            revenue_df["date"] = pd.to_datetime(
                revenue_df["date"],
            )

            revenue_df = revenue_df.set_index("date")

            st.line_chart(
                revenue_df["revenue"],
                use_container_width=True,
            )

        else:
            st.info("No revenue data available for this period.")

    with chart_col2:
        st.markdown(
            """
            <div class="panel-title">Orders by Status</div>
            <div class="panel-caption">
                Distribution of orders by their current status.
            </div>
            """,
            unsafe_allow_html=True,
        )

        if status_data:
            status_df = pd.DataFrame(
                status_data,
                columns=[
                    "Status",
                    "Orders",
                ],
            )

            st.bar_chart(
                status_df.set_index("Status"),
                use_container_width=True,
            )

        else:
            st.info("No order status data available.")

    # --------------------------------------------------------
    # TOP PRODUCTS
    # --------------------------------------------------------

    st.divider()

    st.markdown(
        """
        <div class="panel-title">Top-Selling Products</div>
        <div class="panel-caption">
            Products ranked by units sold and generated revenue.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if top_products:
        products_df = pd.DataFrame(
            top_products,
            columns=[
                "Product",
                "Units Sold",
                "Revenue",
            ],
        )

        products_df["Revenue"] = products_df["Revenue"].apply(
            lambda value: f"${value:,.2f}"
        )

        st.dataframe(
            products_df,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("No product sales available for this period.")

    # --------------------------------------------------------
    # RECENT ORDERS
    # --------------------------------------------------------

    st.divider()

    st.markdown(
        """
        <div class="panel-title">Recent Orders</div>
        <div class="panel-caption">
            Latest orders included in the selected period.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if recent_orders:
        orders_df = pd.DataFrame(
            recent_orders,
            columns=[
                "Order ID",
                "Date",
                "Customer",
                "Status",
                "Amount",
            ],
        )

        orders_df["Amount"] = orders_df["Amount"].apply(
            lambda value: f"${value:,.2f}"
        )

        st.dataframe(
            orders_df,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("No recent orders available.")

    # --------------------------------------------------------
    # ETL PIPELINE STATUS
    # --------------------------------------------------------

    st.divider()

    st.markdown(
        """
        <div class="pipeline-header">
            <div class="pipeline-icon">⚙️</div>
            <div>
                <div class="panel-title">Data Pipeline</div>
                <div class="panel-caption" style="margin-bottom:0;">
                    Latest synchronization and ingestion status.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if last_run:
        run_id = last_run.id
        status = last_run.status
        rows = last_run.rows_processed
        started = last_run.started_at

        if status == "SUCCESS":
            st.markdown(
                '<span class="status-pill status-success">'
                '●  Synchronization successful'
                '</span>',
                unsafe_allow_html=True,
            )
            st.caption(f"{rows} rows processed in the latest run.")

        elif status == "FAILED":
            st.markdown(
                '<span class="status-pill status-failed">'
                '●  Synchronization failed'
                '</span>',
                unsafe_allow_html=True,
            )

            if last_run.error_message:
                st.caption(f"Error: {last_run.error_message}")

        else:
            st.markdown(
                f'<span class="status-pill status-running">'
                f'●  {status}'
                f'</span>',
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        status_col1, status_col2, status_col3 = st.columns(3)

        with status_col1:
            st.markdown(
                f"""
                <div class="pipeline-stat-label">Run</div>
                <div class="pipeline-stat-value">#{run_id}</div>
                """,
                unsafe_allow_html=True,
            )

        with status_col2:
            st.markdown(
                f"""
                <div class="pipeline-stat-label">Rows processed</div>
                <div class="pipeline-stat-value">{rows:,}</div>
                """,
                unsafe_allow_html=True,
            )

        with status_col3:
            st.markdown(
                f"""
                <div class="pipeline-stat-label">Started</div>
                <div class="pipeline-stat-value">{started}</div>
                """,
                unsafe_allow_html=True,
            )

    else:
        st.info("No ETL runs have been recorded yet.")
