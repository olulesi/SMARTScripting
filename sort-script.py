import pandas as pd

# this is to check the csv given has the correct amount of licences and is sorted by state

def sort_and_add_record_number(input_file, output_file):
    # Read CSV file
    df = pd.read_csv(input_file, skip_blank_lines=True)
    
    # Drop duplicate headers that might have been included in the data
    df = df[df['Name'] != 'Name']
    
    # Sort by 'States' column
    df.sort_values(by='States', inplace=True)
    
    # Reset index and add a record number column
    df.insert(0, 'Record Number', range(1, len(df) + 1))
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    
    print(f"Sorted CSV with record numbers saved as {output_file}")

# File paths
input_file = "/Users/tobilesi/Projects/GeoPandas/total-mineral-lists.csv"
output_file = "total-license-list-v1.csv"

# Run function
sort_and_add_record_number(input_file, output_file)
