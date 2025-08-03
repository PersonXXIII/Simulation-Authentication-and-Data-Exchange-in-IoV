import pandas as pd

# Read the CSV file
data = pd.read_csv('Data.csv')

# Remove spaces from the VIN column
data['VIN'] = data['VIN'].str.replace(" ", "")

# Save the updated dataframe to a new CSV
data.to_csv('Updated_Data.csv', index=False)
