import streamlit as st
import pandas as pd
import os
import pydeck as pdk

from urllib.error import URLError

st.set_page_config(page_title="Map Test", layout="wide")
st.title('My Map')


@st.cache
def from_data_file(filename):
    url = (
        "http://raw.githubusercontent.com/streamlit/"
        "example-data/master/hello/v1/%s" % filename)
    return pd.read_json(url)

# dataPath2 = "C:\\Users\\louie\\OneDrive\\Desktop\\repo\\DeltekMap\\DeltekMapScirpts"
# csv_file = "DeltekMapLayer.csv"
# fullCSV = os.path.join(dataPath2, csv_file)
# df2 = pd.read_csv(
#     fullCSV,
#     dtype={
#         "Name": "object",
#         "WBS1": "object",
#         "FullProjectName": "object",
#         "StageDescription": "object",
#         "Status": "object",
#         "Address": "object",
#         "City": "object",
#         "State": "object",
#         "Zip": "object",
#         "Latitude": float,
#         "Longitude": float,
#         "Score": float,
#         "PrimaryServiceLine": "object",
#         "BusinessUnit": "object",
#         "ProjectType": "object",
#         "MarketSector": "object",
#         "CreateDate": "object",
#         "WinLossDate": "object",
#         "Organization": "object",
#         "ClientAlpha": "object",
#         "BillingClientAlpha": "object",
#         "BillingClientContact": "object",
#         "PlanStartDate": "object",
#         "PlanEndDate": "object",
#         "PrincipalinCharge": "object",
#         "ProjectManager": "object",
#         "ProjectManagerEmail": "object",
#         "ProjectCoordinator": "object",
#         "RegionalVicePresident": "object",
#         "AssociatePM": "object",
#         "Biller": "object",
#         "BusinessUnitDirector": "object",
#         "AccountManagerforPrimaryClient": "object",
#         "AccountManagerforBillingClient": "object",
#         "TechnicalLeader": "object",
#         "ProposalSpecialist": "object",
#         "BusinessDevelopmentLead": "object",
#         "AltBusinessDevelopmentLead": "object",
#         "EstimatedFee": float,
#         "Revenue": float,
#         "CorpCommAssistanceRequired": "object",
#         "CorpCommAsstRequestDate": "object",
#         "URL": "object",
#         "UDrive": "object",
#         "OVERLAP": "object",
#         "IsNotified": "object",
#     },
# )
# st.map(df2)


try:
    ALL_LAYERS = {
        "Bike Rentals": pdk.Layer(
            "HexagonLayer",
            data=from_data_file("bike_rental_stats.json"),
            get_position=["lon", "lat"],
            radius=200,
            elevation_scale=4,
            elevation_range=[0, 1000],
            extruded=True,
        ),
        "Bart Stop Exits": pdk.Layer(
            "ScatterplotLayer",
            data=from_data_file("bart_stop_stats.json"),
            get_position=["lon", "lat"],
            get_color=[200, 30, 0, 160],
            get_radius="[exits]",
            radius_scale=0.05,
        ),
        "Bart Stop Names": pdk.Layer(
            "TextLayer",
            data=from_data_file("bart_stop_stats.json"),
            get_position=["lon", "lat"],
            get_text="name",
            get_color=[0, 0, 0, 200],
            get_size=15,
            get_alignment_baseline="'bottom'",
        ),
        "Outbound Flow": pdk.Layer(
            "ArcLayer",
            data=from_data_file("bart_path_stats.json"),
            get_source_position=["lon", "lat"],
            get_target_position=["lon2", "lat2"],
            get_source_color=[200, 30, 0, 160],
            get_target_color=[200, 30, 0, 160],
            auto_highlight=True,
            width_scale=0.0001,
            get_width="outbound",
            width_min_pixels=3,
            width_max_pixels=30,
        ),
    }
    st.sidebar.markdown('### Map Layers')
    selected_layers = [
        layer for layer_name, layer in ALL_LAYERS.items()
        if st.sidebar.checkbox(layer_name, True)]
    if selected_layers:
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state={"latitude": 37.76,
                                "longitude": -122.4, "zoom": 11, "pitch": 50},
            layers=selected_layers,
        ))
    else:
        st.error("Please choose at least one layer above.")
except URLError as e:
    st.error("""
        **This demo requires internet access.**

        Connection error: %s
    """ % e.reason)

# observable("Trader Joes Voronoi Map",
#            notebook="@mbostock/u-s-voronoi-map-o-matic",
#            targets=["map"],
#            redefine={
#                "data": df3[["lon", "lat", "Name"]].to_dict(orient="records")
#            }
#            )
