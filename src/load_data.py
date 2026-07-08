import pandas as pd

# load dataset
data = pd.read_csv("data/creditcard.csv")

print(data.head())
print(data.shape)
print(data["Class"].value_counts())
