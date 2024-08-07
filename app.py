import streamlit as st
import pandas as pd
import plotly.graph_objects as go

import pickle

with open('random_forest_model.pkl', 'rb') as f:
    rf = pickle.load(f)

st.set_page_config(
    page_title='Geo-Mechanical Properties Prediction',
    page_icon='✅',
    layout='wide'
)

# Custom CSS for styling
st.markdown(
    """
    <style>
    .title {
        font-size: 36px;
        font-weight: bold;
        color: #2C3E50;
        margin-top: 0;
        padding-top: 0;
    }
    .subheader {
        font-size: 32px; /* Increased font size */
        font-weight: bold;
        color: #34495E;
        margin-top: 20px;
        padding-top: 0;
    }
    .content {
        margin-top: 30px;
        padding-top: 0;
    }
    .sidebar .sidebar-content {
        background-color: #ECF0F1;
        padding: 20px;
    }
    .stButton>button {
        background-color: #3498DB;
        color: white;
    }
    /* Table styles */
    .dataframe thead th {
        font-weight: bold;
        color: #2C3E50;
    }
    .dataframe tbody td {
        color: #34495E;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<h1 class="title">Geo-Mechanical Properties Prediction</h1>', unsafe_allow_html=True)

# Sidebar for file upload
st.sidebar.header("Upload CSV")
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file

if st.session_state.uploaded_file is not None:
    # Read the CSV file
    data = pd.read_csv(st.session_state.uploaded_file)

    # Set the depth column as the index
    if 'Depth' in data.columns:
        data.set_index('Depth', inplace=True)

    # Read the other dataframe with the actual column
    actual_data = pd.read_csv("Comparing_csv.csv")

    # Add the 'actual column' from the other dataframe to input_data
    data['Actual Poisson Ratio(u)'] = pd.Series(actual_data['Actual Poisson Ratio(u)'].values, index=data.index)
    data['Actual Young Modulus(E)'] = pd.Series(actual_data['Actual Young Modulus(E)'].values, index=data.index)

    # Assuming the CSV has columns: resistivity, gamma_ray, total_porosity, bulk_density
    input_data = data[['Resistivity', 'Gamma Ray', 'Total Porosity', 'Bulk Density']]

    # Predict the values
    predictions = rf.predict(input_data)
    data['Predicted Poisson Ratio(u)'] = predictions[:, 0]
    data['Predicted Young Modulus(E)'] = predictions[:, 1]


    data['% Error in Predicted Poisson Ratio(u)'] = abs((data['Actual Poisson Ratio(u)'] - data['Predicted Poisson Ratio(u)']) / data['Actual Poisson Ratio(u)']) * 100
    data['% Error in Predicted Young Modulus(E)'] = abs((data['Actual Young Modulus(E)'] - data['Predicted Young Modulus(E)']) / data['Actual Young Modulus(E)']) * 100


    # Formatting percentage error as percent
    data['% Error in Predicted Poisson Ratio(u)'] = data['% Error in Predicted Poisson Ratio(u)'].apply(lambda x: f"{x:.2f}")
    data['% Error in Predicted Young Modulus(E)'] = data['% Error in Predicted Young Modulus(E)'].apply(lambda x: f"{x:.2f}")

    # Plot for Poisson Ratio(u)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=data.index, y=data['Actual Poisson Ratio(u)'], mode='lines', name='Actual  Poisson’s Ratio', line=dict(color='blue')))
    fig2.add_trace(go.Scatter(x=data.index, y=data['Predicted Poisson Ratio(u)'], mode='lines', name='Predicted  Poisson’s Ratio', line=dict(color='red')))
    fig2.update_layout(
        title="Actual vs Predicted Poisson Ratio",
        xaxis_title="Depth (ft)",
        yaxis_title="Dynamic Poisson’s Ratio ϑ",
        legend_title="Legend",
        template="plotly_white",
        width=1000,  # Adjust plot width
        height=400,  # Adjust plot height
        margin=dict(l=40, r=10, t=40, b=30)
    )

    # Plot for Young Modulus(E)
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=data.index, y=data['Actual Young Modulus(E)'], mode='lines', name="Actual Young's Modulus", line=dict(color='blue')))
    fig1.add_trace(go.Scatter(x=data.index, y=data['Predicted Young Modulus(E)'], mode='lines', name="Predicted Young's Modulus", line=dict(color='red')))
    fig1.update_layout(
        title="Actual vs Predicted Young's Modulus",
        xaxis_title="Depth (ft)",
        yaxis_title="Young’s Modulus (GPa)",
        legend_title="Legend",
        template="plotly_white",
        width=1000,  # Adjust plot width
        height=400,  # Adjust plot height
        margin=dict(l=40, r=10, t=40, b=30)
    )

    # Layout for the first plot and table
    col1, col2 = st.columns([2, 2])
    with col1:
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        st.dataframe(data[['Actual Poisson Ratio(u)', 'Predicted Poisson Ratio(u)', '% Error in Predicted Poisson Ratio(u)']],
                     use_container_width=True)

    # Layout for the second plot and table
    col3, col4 = st.columns([2, 2])
    with col3:
        st.plotly_chart(fig1, use_container_width=True)
    with col4:
        st.dataframe(data[['Actual Young Modulus(E)', 'Predicted Young Modulus(E)', '% Error in Predicted Young Modulus(E)']],
                     use_container_width=True)
