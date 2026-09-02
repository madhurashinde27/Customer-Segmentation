import pandas as pd
import numpy as np

# Load Dataset
df = pd.read_excel("data/Online Retail.xlsx")

# First 5 rows
print(df.head())

# Dataset shape
print("Dataset Shape:", df.shape)

# Columns
print("\nColumns:")
print(df.columns)


# Data Types
print("\nData Types:")
print(df.dtypes)

# Missing Values
print("\nMissing Values:")
print(df.isnull().sum())

# Duplicate Rows
print("\nDuplicate Rows:", df.duplicated().sum())

# ==============================
# DATA CLEANING
# ==============================

# 1. Remove duplicate rows
df = df.drop_duplicates()

# 2. Remove rows where CustomerID is missing
df = df.dropna(subset=["CustomerID"])

# 3. Remove cancelled transactions
df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]

# 4. Remove invalid Quantity and UnitPrice
df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]

# 5. Create Revenue column
df["Revenue"] = df["Quantity"] * df["UnitPrice"]

# Check cleaned data
print("\nAfter Cleaning:")
print("Dataset Shape:", df.shape)

print("\nMissing Values:")
print(df.isnull().sum())

print("\nFirst 5 Cleaned Rows:")
print(df.head())


# ==============================
# RFM ANALYSIS
# ==============================

# Set analysis date as the day after the last transaction
analysis_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

# Create RFM table
rfm = df.groupby("CustomerID").agg({
    "InvoiceDate": lambda x: (analysis_date - x.max()).days,
    "InvoiceNo": "nunique",
    "Revenue": "sum"
})

# Rename columns
rfm.columns = ["Recency", "Frequency", "Monetary"]

# Display RFM data
print("\nRFM Analysis:")
print(rfm.head())

# RFM summary
print("\nRFM Shape:", rfm.shape)

print("\nRFM Statistics:")
print(rfm.describe())


# ==============================
# RFM VISUALIZATION
# ==============================

import matplotlib.pyplot as plt

# Create 3 graphs in one window
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Recency
axes[0].hist(rfm["Recency"], bins=30)
axes[0].set_title("Recency Distribution")
axes[0].set_xlabel("Days Since Last Purchase")
axes[0].set_ylabel("Number of Customers")

# Frequency
axes[1].hist(rfm["Frequency"], bins=30)
axes[1].set_title("Frequency Distribution")
axes[1].set_xlabel("Number of Purchases")
axes[1].set_ylabel("Number of Customers")

# Monetary
axes[2].hist(rfm["Monetary"], bins=30)
axes[2].set_title("Monetary Distribution")
axes[2].set_xlabel("Total Spending")
axes[2].set_ylabel("Number of Customers")

plt.tight_layout()
plt.show()

# ==============================
# PREPARE RFM FOR K-MEANS
# ==============================

from sklearn.preprocessing import StandardScaler

# Log transformation
rfm_log = np.log1p(rfm)

# Standardize the data
scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm_log)

# Convert back to DataFrame
rfm_scaled = pd.DataFrame(
    rfm_scaled,
    columns=["Recency", "Frequency", "Monetary"],
    index=rfm.index
)

print("\nScaled RFM Data:")
print(rfm_scaled.head())

print("\nScaled RFM Shape:", rfm_scaled.shape)


# ==============================
# ELBOW METHOD
# ==============================

from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

inertia = []

for k in range(2, 11):
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(rfm_scaled)
    inertia.append(kmeans.inertia_)

# Plot Elbow Curve
plt.figure(figsize=(8, 5))
plt.plot(range(2, 11), inertia, marker="o")
plt.title("Elbow Method for Optimal Number of Clusters")
plt.xlabel("Number of Clusters (K)")
plt.ylabel("Inertia")
plt.xticks(range(2, 11))
plt.grid()
plt.show()


# ==============================
# K-MEANS CUSTOMER SEGMENTATION
# ==============================

# Create K-Means model
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)

# Fit model and assign clusters
rfm_scaled["Cluster"] = kmeans.fit_predict(rfm_scaled)

# Add cluster number to original RFM data
rfm["Cluster"] = rfm_scaled["Cluster"]

# Display customers with clusters
print("\nCustomer Segments:")
print(rfm.head(10))

# Number of customers in each cluster
print("\nCustomers in Each Cluster:")
print(rfm["Cluster"].value_counts().sort_index())


# ==============================
# CLUSTER PROFILING
# ==============================

cluster_summary = rfm.groupby("Cluster").agg({
    "Recency": "mean",
    "Frequency": "mean",
    "Monetary": "mean"
}).round(2)

print("\nCluster Summary:")
print(cluster_summary)


# ==============================
# CUSTOMER SEGMENT VISUALIZATION
# ==============================

import matplotlib.pyplot as plt

cluster_counts = rfm["Cluster"].value_counts().sort_index()

plt.figure(figsize=(8, 5))
plt.bar(cluster_counts.index.astype(str), cluster_counts.values)

plt.title("Number of Customers in Each Segment")
plt.xlabel("Customer Segment")
plt.ylabel("Number of Customers")

plt.show()


# ==============================
# BUSINESS INSIGHTS
# ==============================

cluster_summary = rfm.groupby("Cluster").agg({
    "Recency": "mean",
    "Frequency": "mean",
    "Monetary": "mean"
}).round(2)

cluster_summary["Customers"] = rfm.groupby("Cluster").size()

print("\nFinal Customer Segment Analysis:")
print(cluster_summary)


# ==============================
# SAVE FINAL CUSTOMER SEGMENTS
# ==============================

# Create output folder
import os

os.makedirs("output", exist_ok=True)

# Save RFM customer segments
rfm.to_csv("output/customer_segments.csv")

print("\nFinal customer segmentation saved successfully!")
print("File: output/customer_segments.csv")