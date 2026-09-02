import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ==============================
# PAGE SETTINGS
# ==============================

st.set_page_config(
    page_title="Customer Segmentation Dashboard",
    page_icon="📊",
    layout="wide"
)

# ==============================
# LOAD DATA
# ==============================

BASE_DIR = Path(__file__).resolve().parent.parent
csv_path = BASE_DIR / "output" / "customer_segments.csv"

df = pd.read_csv(csv_path)

# Customer ID as integer
df["CustomerID"] = df["CustomerID"].astype(int)

# ==============================
# SEGMENT NAMES
# ==============================

segment_names = {
    0: "High-Value / Loyal",
    1: "At-Risk / Low-Value",
    2: "Potential Customers",
    3: "Regular Customers"
}

df["Segment"] = df["Cluster"].map(segment_names)

# ==============================
# TITLE
# ==============================

st.title("📊 Customer Segmentation Dashboard")

st.write(
    "Customer segmentation based on RFM analysis and K-Means clustering."
)

st.divider()

# ==============================
# SIDEBAR FILTER
# ==============================

st.sidebar.header("🔎 Filters")

segments = ["All Segments"] + sorted(df["Segment"].unique().tolist())

selected_segment = st.sidebar.selectbox(
    "Select Customer Segment",
    segments
)

if selected_segment == "All Segments":
    filtered_df = df.copy()
else:
    filtered_df = df[df["Segment"] == selected_segment]

# ==============================
# KPI CARDS
# ==============================

total_customers = filtered_df["CustomerID"].nunique()
total_revenue = filtered_df["Monetary"].sum()
avg_spending = filtered_df["Monetary"].mean()
avg_frequency = filtered_df["Frequency"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "👥 Total Customers",
    f"{total_customers:,}"
)

col2.metric(
    "💰 Total Revenue",
    f"£{total_revenue:,.2f}"
)

col3.metric(
    "💵 Avg Customer Spend",
    f"£{avg_spending:,.2f}"
)

col4.metric(
    "🔄 Avg Purchase Frequency",
    f"{avg_frequency:.2f}"
)

st.divider()

# ==============================
# SEGMENT SUMMARY
# ==============================

st.subheader("📋 Customer Segment Summary")

summary = filtered_df.groupby("Segment").agg(
    Customers=("CustomerID", "count"),
    Avg_Recency=("Recency", "mean"),
    Avg_Frequency=("Frequency", "mean"),
    Avg_Monetary=("Monetary", "mean")
).round(2)

st.dataframe(
    summary,
    use_container_width=True
)

# ==============================
# CUSTOMER DISTRIBUTION
# ==============================

st.subheader("👥 Customers by Segment")

segment_counts = filtered_df["Segment"].value_counts()

fig, ax = plt.subplots(figsize=(8, 4.5))

ax.bar(
    segment_counts.index,
    segment_counts.values
)

ax.set_xlabel("Customer Segment")
ax.set_ylabel("Number of Customers")
ax.set_title("Customer Distribution by Segment")

plt.xticks(rotation=20)
plt.tight_layout()

st.pyplot(fig, use_container_width=True)

# ==============================
# TWO COLUMN SECTION
# ==============================

col1, col2 = st.columns(2)

# ==============================
# REVENUE BY SEGMENT
# ==============================

with col1:

    st.subheader("💰 Revenue by Segment")

    revenue_by_segment = (
        filtered_df.groupby("Segment")["Monetary"]
        .sum()
        .sort_values(ascending=False)
    )

    fig2, ax2 = plt.subplots(figsize=(7, 4))

    ax2.bar(
        revenue_by_segment.index,
        revenue_by_segment.values
    )

    ax2.set_xlabel("Customer Segment")
    ax2.set_ylabel("Revenue (£)")
    ax2.set_title("Revenue Contribution by Segment")

    plt.xticks(rotation=25)
    plt.tight_layout()

    st.pyplot(fig2, use_container_width=True)


# ==============================
# PURCHASE FREQUENCY
# ==============================

with col2:

    st.subheader("🔄 Purchase Frequency")

    frequency_by_segment = (
        filtered_df.groupby("Segment")["Frequency"]
        .mean()
        .sort_values(ascending=False)
    )

    fig3, ax3 = plt.subplots(figsize=(7, 4))

    ax3.bar(
        frequency_by_segment.index,
        frequency_by_segment.values
    )

    ax3.set_xlabel("Customer Segment")
    ax3.set_ylabel("Average Frequency")
    ax3.set_title("Average Purchase Frequency")

    plt.xticks(rotation=25)
    plt.tight_layout()

    st.pyplot(fig3, use_container_width=True)

# ==============================
# RFM ANALYSIS
# ==============================

st.divider()

st.subheader("📈 RFM Analysis by Segment")

rfm_summary = filtered_df.groupby("Segment")[
    ["Recency", "Frequency", "Monetary"]
].mean().round(2)

# Recency
st.write("### 🕒 Average Recency")

st.bar_chart(
    rfm_summary["Recency"]
)

# Frequency
st.write("### 🔄 Average Frequency")

st.bar_chart(
    rfm_summary["Frequency"]
)

# Monetary
st.write("### 💰 Average Monetary Value")

st.bar_chart(
    rfm_summary["Monetary"]
)

# ==============================
# BUSINESS INSIGHTS
# ==============================

st.divider()

st.subheader("💡 Business Insights")

if selected_segment == "All Segments":

    st.write(
        "• **High-Value / Loyal:** Customers with low recency, "
        "high purchase frequency and high monetary value."
    )

    st.write(
        "• **At-Risk / Low-Value:** Customers with high recency "
        "and relatively low purchase activity."
    )

    st.write(
        "• **Potential Customers:** Customers who have recently "
        "purchased but have lower purchase frequency."
    )

    st.write(
        "• **Regular Customers:** Customers showing moderate "
        "recency, frequency and spending behaviour."
    )

else:

    st.write(
        f"### Selected Segment: {selected_segment}"
    )

    st.write(
        f"Number of customers: **{len(filtered_df):,}**"
    )

    st.write(
        f"Average spending: **£{filtered_df['Monetary'].mean():,.2f}**"
    )

    st.write(
        f"Average purchase frequency: "
        f"**{filtered_df['Frequency'].mean():.2f}**"
    )

# ==============================
# CUSTOMER DATA
# ==============================

st.divider()

st.subheader("📋 Customer Details")

display_columns = [
    "CustomerID",
    "Recency",
    "Frequency",
    "Monetary",
    "Cluster",
    "Segment"
]

st.dataframe(
    filtered_df[display_columns].sort_values(
        "Monetary",
        ascending=False
    ),
    use_container_width=True,
    height=450
)

# ==============================
# FOOTER
# ==============================

st.divider()

st.caption(
    "Customer Segmentation Project | RFM Analysis + K-Means Clustering"
)