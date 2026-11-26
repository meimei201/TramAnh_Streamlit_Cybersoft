import streamlit as st
import pandas as pd

st.set_page_config(
    page_title= 'Ask your CSV',
    page_icon= '📊',
    layout='wide'
)


st.title("Ask your CSV")
st.markdown("Upload your data and ask question in plain English ")

#Sidebar for file upload
with st.sidebar:
    st.header('Data upload')
    uploaded_file=st.file_uploader('Upload a CSV file', type=['csv'])

    if uploaded_file:
        try:
            df=pd.read_csv(uploaded_file)
            st.success(f"Loaded {df.shape[0]} rows x {df.shape[1]} columns")

            #Data Preview
            with st.expander("Preview data"):
                st.dataframe(df.head())
            #Basic statics
            with st.expander("Data summary"):
                col1,col2 = st.columns(2)

                with col1:
                    st.metric("Total rows", df.shape[0])
                    st.metric("Total columns", df.shape[1])

                with col2:
                    st.metric("Memory Usage", f"{df.memory_usage().sum()/1024:.1f} KB")
                    st.metric("Missing Value", df.isnull().sum().sum())

        except Exception as e:  
            st.error(f"Error reading file: {st(e)}")
            st.info("Please make sure your file is a valid CSV format")

    else:
        st.info("Upload a CSV to start analyzing")