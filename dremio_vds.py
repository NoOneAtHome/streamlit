import Dremio.api as dapi
import pandas as pd 
import streamlit as st
import pandas as pd
import json
from streamlit_js_eval import streamlit_js_eval
from st_aggrid import AgGrid, GridOptionsBuilder
from code_editor import code_editor

try:
  st.set_page_config(layout='wide')
except:
  pass

def extract_values(dictionary):
   result = json.loads(dictionary)
   id = result['contentId']
   return id

#df = pd.DataFrame(dapi.getByPath(['nessie','testing']))

#df['contentId'] = df['id'].apply(lambda x: pd.Series(extract_values(x))) 

nav ={}
if 'id' in st.query_params:
 
   id = st.query_params['id']
 
   result = dapi.apiGet(f'catalog/{id}')
   try:
    if result['children'] ==None:
        data =[[result['id'],result['path']]]
        df = pd.DataFrame(data, columns=['id', 'path'])
        folder_df = df[df['type'] == 'CONTAINER']
        dataset_df = df[df['type'] == 'DATASET']
        
        #dataframe[dataframe['Percentage'] > 70] 
    else:
        df = pd.DataFrame(result['children'])
        folder_df = df[df['type'] == 'CONTAINER']
        dataset_df = df[df['type'] == 'DATASET']
   except KeyError:
        data =[[result['id'],result['path']]]
        folder_df = pd.DataFrame(data, columns=['id', 'path'])
      
else:
    df = dapi.getByPath(['Testing','curated'])
    df= pd.DataFrame(df['children'])
    folder_df = df[df['type'] == 'CONTAINER']
    dataset_df = df[df['type'] == 'DATASET']


folder_grid_builder = GridOptionsBuilder.from_dataframe(folder_df)
folder_grid_builder.configure_selection(selection_mode="single", use_checkbox=False)
folder_grid_builder.configure_auto_height(autoHeight=True)
folder_grid_builder.configure_column(field='id', header_name='id')
folder_grid_builder.configure_column(field='path', header_name='Path')
folder_grid_builder.configure_column(field='type', header_name='Path Type')
folder_grid_builder.configure_column(field='')

folder_grid_options = folder_grid_builder.build()

dataset_grid_builder = GridOptionsBuilder.from_dataframe(dataset_df)
dataset_grid_builder.configure_selection(selection_mode="single", use_checkbox=False)
dataset_grid_builder.configure_auto_height(autoHeight=True)
dataset_grid_builder.configure_column(field='id', header_name='id')
dataset_grid_builder.configure_column(field='path', header_name='Path')
dataset_grid_builder.configure_column(field='type', header_name='Path Type')
dataset_grid_builder.configure_column(field='')

dataset_grid_options = dataset_grid_builder.build()

response = AgGrid(data=folder_df, gridOptions=folder_grid_options, key='folder_grid')
if st.button("Next"):
     streamlit_js_eval(js_expressions="parent.window.location.reload()")
dataset_response = AgGrid(data=dataset_df,gridOptions=dataset_grid_options,key='dataset_grid')
selected_data = response.selected_data
if selected_data is None:
   st.write()
else:
   id = response.selected_data['id']
   st.query_params['id'] = id

