import geopandas as gpd
import pandas as pd
import os
import zipfile

# /Users/tobilesi/Projects/GeoPandas/master-csv
# Define paths
input_folder = "/Users/tobilesi/Projects/GeoPandas/master-csv/Kano-state-mining-Licenses"  # Replace with the folder containing ZIP files
kaduna_folder = "/Users/tobilesi/Projects/GeoPandas/master-csv/Kaduna-state-mining-licenses-data"  # Replace with the folder containing ZIP files
plateau_folder = "/Users/tobilesi/Projects/GeoPandas/master-csv/Plateau-Mining-licenses"  # Replace with the folder containing ZIP files
output_csv = "State-mining-Licenses-v3.csv"

# Initialize an empty list to collect data from all shapefiles
all_data = []

# Loop through all ZIP files in the input folder
def process_zip_files(folder_path, state_name):
    for zip_filename in os.listdir(folder_path):
        if zip_filename.endswith(".zip"):
            zip_path = os.path.join(folder_path, zip_filename)
            
            # Extract ZIP contents to a temporary folder
            temp_extract_folder = os.path.join(folder_path, "temp_extracted")
            os.makedirs(temp_extract_folder, exist_ok=True)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_extract_folder)

            # Find the .shp file in the extracted folder
            shp_file = None
            for root, dirs, files in os.walk(temp_extract_folder):
                for file in files:
                    if file.endswith(".shp"):
                        shp_file = os.path.join(root, file)
                        break
            
            if shp_file:
                try:
                    # Read the shapefile
                    gdf = gpd.read_file(shp_file)

                    # Check loaded columns
                    print(f"Processing {zip_filename}")
                    print("Columns:", gdf.columns.tolist())
                    print("Number of records:", len(gdf))

                    # Verify CRS
                    crs_info = gdf.crs.to_string() if gdf.crs else "No CRS"
                    print("CRS:", crs_info)

                    # Add CRS as a new column
                    gdf["CRS"] = crs_info

                    # Convert geometry to WKT (for easy CSV storage)
                    gdf["geometry"] = gdf["geometry"].apply(lambda geom: geom.wkt if geom else None)

                    # Add filename reference to track origin
                    gdf["Source_File"] = zip_filename

                    # Add 'State' column with dynamic value
                    gdf["State"] = state_name

                    # Add 'LGA' column blank
                    gdf["LGA"] = ""

                    gdf["Minerals"] = ""

                    # Convert cadastral units to square kilometers
                    if "Cadastral_" in gdf.columns:
                        gdf["Square_KM_Units"] = gdf["Cadastral_"] * 0.2

                    # Collect the dataframe
                    all_data.append(gdf)

                except Exception as e:
                    print(f"Error processing {zip_filename}: {e}")

            # Clean up extracted files after processing
            for root, dirs, files in os.walk(temp_extract_folder, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(temp_extract_folder)

# Process original ZIP files with state 'Kano'
process_zip_files(input_folder, "Kano")

# Process additional ZIP files with state 'Kaduna'
process_zip_files(kaduna_folder, "Kaduna")

# Process additional ZIP files with state 'Plateua'
process_zip_files(plateau_folder, "Plateau")

# Combine all data into one DataFrame
if all_data:
    final_df = pd.concat(all_data, ignore_index=True)
    final_df.insert(0, "Record_Number", range(1, len(final_df) + 1))  # Add record numbers
    final_df.to_csv(output_csv, index=False)
    print(f"Successfully merged all shapefiles into {output_csv}")
else:
    print("No shapefiles were processed.")
