import Dremio.api as dapi
import pandas as pd
import streamlit as st
import pandas as pd
import json
from streamlit_js_eval import streamlit_js_eval
from st_aggrid import AgGrid, GridOptionsBuilder
from code_editor import code_editor

try:
    st.set_page_config(layout="wide")
except:
    pass


def extract_values(dictionary):
    result = json.loads(dictionary)
    id = result["contentId"]
    return id


# df = pd.DataFrame(dapi.getByPath(['nessie','testing']))

# df['contentId'] = df['id'].apply(lambda x: pd.Series(extract_values(x)))
folder_on_select = "rerun"
nav = {}
st.markdown(
    """
            <style>
                div[data-testid="column"] {
                    width: fit-content !important;
                    flex: unset;
                }
                div[data-testid="column"] * {
                    width: fit-content !important;
                }
            </style>
            """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("home"):
        st.query_params["id"] = "0"
with col2:
    if st.button("Previous"):
        st.query_params["id"] = st.query_params["prev"]

if "id" not in st.query_params or st.query_params["id"] == "0":
    st.query_params["prev"] = 0
    st.query_params["id"] = 0
    df = dapi.getByPath(["Testing", "curated"])
    df = pd.DataFrame(df["children"])
    folder_df = df[df["type"] == "CONTAINER"]
    dataset_df = df[df["type"] == "DATASET"]
    function_df = df[df["containerType"] == "FUNCTION"]

else:
    id = st.query_params["id"]

    result = dapi.apiGet(f"catalog/{id}")
    try:
        if len(result["children"]) > 0:
            data = [[result["id"], result["path"]]]
            df = pd.DataFrame(result["children"])
            folder_df = df[
                (df["type"] == "CONTAINER") & (df["containerType"] == "FOLDER")
            ]

            if folder_df.empty:
                data = [[result["id"], result["path"]]]
                folder_df = pd.DataFrame(data, columns=["id", "path"])
                folder_on_select = "ignore"
            else:
                folder_on_select = "rerun"

            dataset_df = df[df["type"] == "DATASET"]
            function_df = df[df["containerType"] == "FUNCTION"]

        else:
            df = pd.DataFrame.from_dict(result, orient="index")
            ffolder_df = df[
                (df["type"] == "CONTAINER") & (df["containerType"] == "FOLDER")
            ]
            dataset_df = df[df["type"] == "DATASET"]
            function_df = df[df["containerType"] == "FUNCTION"]

    except KeyError:
        data = [[result["id"], result["path"]]]
        folder_on_select = "ignore"
        folder_df = pd.DataFrame(data, columns=["id", "path"])
        dataset_df = pd.DataFrame()
        # function_df = df[df["type"] == "FUNCTION"]

st.header("Folders")
response = st.dataframe(
    folder_df,
    use_container_width=True,
    hide_index=True,
    on_select=folder_on_select,
    selection_mode="single-row",
)

if st.button("Next"):
    streamlit_js_eval(js_expressions="parent.window.location.reload()")

st.header("Datasets")
if dataset_df.empty or len(dataset_df) == 0:
    # if 1 != 1:
    st.warning("No Datesets")
else:
    dataset_response = st.dataframe(
        dataset_df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row",
    )
st.header("Functions")
if function_df.empty or len(function_df) == 0:
    st.warning("No Functions")
else:
    function_response = st.dataframe(
        function_df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row",
    )


if folder_on_select == "rerun":
    selected_data = response.selection.rows

    if len(selected_data) == 0:
        st.write()
    else:
        selected_data = response.selection.rows
        filtered_df = folder_df.iloc[selected_data]
        prev = st.query_params["id"]
        st.query_params["prev"] = prev
        id = filtered_df.iloc[0]["id"]
        st.query_params["id"] = id
