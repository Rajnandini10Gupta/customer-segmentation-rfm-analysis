import pandas as pd

# Load the dataset
df = pd.read_csv("rfm_data.csv")
df["PurchaseDate"] = pd.to_datetime(df["PurchaseDate"])

# Set reference date
reference_date = df["PurchaseDate"].max() + pd.Timedelta(days=1)

# Calculate RFM metrics
rfm = df.groupby("CustomerID").agg(
    Recency=("PurchaseDate", lambda x: (reference_date - x.max()).days),
    Frequency=("OrderID", "nunique"),
    Monetary=("TransactionAmount", "sum")
).reset_index()

# Calculate RFM scores
rfm["R_Score"] = pd.qcut(
    rfm["Recency"].rank(method="first"),
    5, labels=[5, 4, 3, 2, 1]
).astype(int)

rfm["F_Score"] = pd.qcut(
    rfm["Frequency"].rank(method="first"),
    5, labels=[1, 2, 3, 4, 5]
).astype(int)

rfm["M_Score"] = pd.qcut(
    rfm["Monetary"].rank(method="first"),
    5, labels=[1, 2, 3, 4, 5]
).astype(int)

# Assign customer segments
def assign_segment(row):
    if row["R_Score"] >= 4 and row["F_Score"] >= 4 and row["M_Score"] >= 4:
        return "Champions"
    elif row["R_Score"] >= 3 and row["F_Score"] >= 3:
        return "Loyal Customers"
    elif row["R_Score"] >= 4 and row["F_Score"] <= 2:
        return "Potential Loyalists"
    elif row["R_Score"] <= 2 and row["F_Score"] >= 3:
        return "At Risk"
    else:
        return "Needs Attention"

rfm["Segment"] = rfm.apply(assign_segment, axis=1)

# Display results
print("Customer segment counts:")
print(rfm["Segment"].value_counts())

print("\nTotal customers segmented:", len(rfm))
# Save RFM analysis results
rfm.to_csv("python_analysis/rfm_results.csv", index=False)

print("\nRFM results saved successfully!")
import matplotlib.pyplot as plt

segment_counts = rfm["Segment"].value_counts()

plt.figure(figsize=(9, 5))
segment_counts.plot(kind="bar")

plt.title("Customer Segmentation - RFM Analysis")
plt.xlabel("Customer Segment")
plt.ylabel("Number of Customers")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("python_analysis/customer_segments.png", dpi=300, bbox_inches="tight")
plt.show()
# Summarize RFM metrics by customer segment
summary = rfm.groupby("Segment").agg(
    Customer_Count=("CustomerID", "count"),
    Average_Recency=("Recency", "mean"),
    Average_Frequency=("Frequency", "mean"),
    Total_Monetary=("Monetary", "sum")
).round(2)

print("\nRFM Segment Summary:")
print(summary)

# Save the summary
summary.to_csv("python_analysis/rfm_segment_summary.csv")

print("\nSegment summary saved successfully!")
# Total Monetary Value by Customer Segment

monetary_by_segment = rfm.groupby("Segment")["Monetary"].sum()

plt.figure(figsize=(10, 6))
monetary_by_segment.sort_values(ascending=False).plot(
    kind="bar",
    color="teal"
)

plt.title("Total Monetary Value by Customer Segment")
plt.xlabel("Customer Segment")
plt.ylabel("Total Monetary Value")
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig("python_analysis/monetary_by_segment.png")
plt.show()