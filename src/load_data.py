import os
import pandas as pd

# Define dataset path relative to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "creditcard.csv")

# Load dataset
data = pd.read_csv(DATA_PATH)

print(data.head())
print(data.shape)
print(data["Class"].value_counts())
