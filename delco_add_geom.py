import asyncio
import pandas as pd
import requests
from aiohttp import ClientSession, ClientTimeout
import aiohttp

async def main():
    url = "https://gis.delcopa.gov/arcgis/rest/services/Parcels/Parcels_Public_Access/MapServer/0/query"

    # Specify the parameters for the query
    muni_code = "43"
    muni = "swarthmore"
    params = {
        "where": "MUNICIPALITY = " + muni_code,
        "outFields": "*",
        "returnGeometry": "true",
        "f": "json",
        "resultOffset": 0,  # Start with the first record
        "resultRecordCount": 2000,  # Number of records to retrieve per request
    }

    dfs_to_query = []
    query_df = pd.DataFrame()

    while True:
        # Send the GET request to the ArcGIS Feature Service
        response = requests.get(url, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            # Extract the features from the response
            features = data.get("features", [])
            # Break the loop if there are no more records
            if not features:
                break
            # Create a DataFrame from the features
            df = pd.json_normalize(features)
            # Extract 'attributes' and 'geometry' data
            current_columns = df.columns
            new_columns = {col: col.split('.')[-1] for col in current_columns}
            df.rename(columns=new_columns, inplace=True)
            df = df[['PARID', 'rings']]
            # Rename the columns
            df.rename(columns={'PARID': 'Parcel_ID', 'rings': 'geometry'}, inplace=True)
            # Append the DataFrame to the list
            dfs_to_query.append(df)
            # Increment the result offset for the next iteration
            params["resultOffset"] += params["resultRecordCount"]
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            break

    # Concatenate all DataFrames in the list into the combined DataFrame
    query_df = pd.concat(dfs_to_query, ignore_index=True)
    print(query_df)
    query_df['Parcel_ID'] = query_df['Parcel_ID'].astype(str).str.strip()

    # Read the existing CSV file
    csv_file_path = muni + "_parcels.csv"
    try:
        csv_df = pd.read_csv(csv_file_path)
        csv_df['Parcel_ID'] = csv_df['Parcel_ID'].astype(str).str.strip()
        csv_df.drop_duplicates(subset='Parcel_ID', keep='last', inplace=True)
    except FileNotFoundError:
        csv_df = pd.DataFrame(columns=['Parcel_ID', 'geometry'])
        csv_df.to_csv(csv_file_path, index=False)

    # Merge the data based on Parcel_ID
    merged_df = pd.merge(csv_df, query_df, on='Parcel_ID', how='outer')

    # Save the merged DataFrame back to CSV
    merged_df.to_csv(csv_file_path, index=False)

    print(f"Merged data saved to {csv_file_path}")

asyncio.run(main())