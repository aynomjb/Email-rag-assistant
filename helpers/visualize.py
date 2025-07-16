import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

def visualize(path):
    full_path = os.path.join("results", path)
    df = pd.read_csv(full_path)

    # Optional: add fake timestamp if missing
    if "timestamp" not in df.columns:
        df["timestamp"] = pd.date_range(start=datetime.now(), periods=len(df), freq="T")
    
    

    plt.figure(figsize=(10, 4))
    sns.lineplot(x="timestamp", y="f1_score", data=df, marker="o", color="green")
    plt.title("F1 Score Over Time")
    plt.xticks(rotation=45)
    plt.ylabel("F1 Score")
    plt.tight_layout()
    plt.grid(True)
    plt.show()

    plt.figure(figsize=(6, 4))
    sns.histplot(df["f1_score"], bins=10, kde=True, color="skyblue")
    plt.title("Distribution of F1 Scores")
    plt.xlabel("F1 Score")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    low_scores = df[df["f1_score"] < 0.6]
    print("⚠️ Low-accuracy queries:")
    print(low_scores[["question", "f1_score", "predicted_answer"]])
