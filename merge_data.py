import pandas as pd

# Load the files
print("Reading files...")
csv_df = pd.read_csv('cleaned_catnat_final.csv')
xlsx_df = pd.read_excel('algerian_seismic_risk_all_wilayas.xlsx')

# Normalize the join keys to integers
csv_df['Wilaya_Number'] = pd.to_numeric(csv_df['Wilaya_Number'], errors='coerce')
xlsx_df['Code'] = pd.to_numeric(xlsx_df['Code'], errors='coerce')

# Merge the dataframes
print("Merging data...")
merged_df = pd.merge(
    csv_df, 
    xlsx_df, 
    left_on='Wilaya_Number', 
    right_on='Code', 
    how='left'
)

# Drop the redundant 'Code' and 'Wilaya' columns from the XLSX 
# (since we already have Wilaya_Number and Wilaya_Name)
merged_df = merged_df.drop(columns=['Code', 'Wilaya'])

# Save the result
output_file = 'catnat_with_seismic_data.csv'
print(f"Saving to {output_file}...")
merged_df.to_csv(output_file, index=False)
print("Done!")
