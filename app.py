import streamlit as st
import pandas as pd
import openai

st.set_page_config(
    page_title= 'Ask your CSV',
    page_icon= '📊',
    layout='wide'
)

#Initialize OpenAi Clients
client=openai.OpenAI(api_key=st.secrets['OPENAI_API_KEY'])


#Session state initialization
if 'messages' not in st.session_state:
    st.session_state.messages=[]
if 'df' not in st.session_state:
    st.session_state.df=None
if'data_summary' not in st.session_state:
    st.session_state.data_summary=None



st.title("Ask your CSV")
st.markdown("Upload your data and ask question in plain English ")

#Sidebar for file upload
with st.sidebar:
    st.header('Data upload')
    uploaded_file=st.file_uploader('Upload a CSV file', type=['csv'])

    if uploaded_file:
        try:
            df=pd.read_csv(uploaded_file)
            st.session_state.df = df
            st.success(f"Loaded {df.shape[0]} rows x {df.shape[1]} columns")

            #Create data summary for token optimization
            st.session_state.data_summary={
                "shapes": df.shape,
                "columns": df.columns.tolist(),
                "dtypes": df.dtypes.to_dict(),
                "samples":df.head(3).to_dict(),
                "stats": df.describe().to_dict() if not df.empty else {}
            }

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


#Main chat interface
if st.session_state.df is not None:
    #Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])

    #Chat input
    user_input=st.chat_input("Ask a question about your data")

    if user_input:
        #Add user's messages to history
        st.session_state.messages.append({'role':'user','content':user_input})
        #Display user message
        with st.chat_message('user'):
            st.markdown(user_input)

        #Prepare data context with token optimazation
        df=st.session_state.df #Gan nguoc lai df cua session vao bien df
        if len(df)>100:
            data_context= f""""
            Dataset Shape: {st.session_state.data_summary['shapes']},
            Columns: {' , '.join(st.session_state.data_summary['columns'])}
            Data types: {st.session_state.data_summary['dtypes']}
            Samples: {st.session_state.data_summary['samples']}
            Basic statistics: {st.session_state.data_summary['stats']}         
            """

        else:
            data_context = f""""
            Full dataset:
            {df.to_string()} 
            """


        #System Prompt
        system_prompt = f"""
        You are a helpful data analyst assistant.
        The user has uploaded a CSV file with the following information:
        {data_context} 

        The data is loaded in a Pandas Dataframe called `df`.

        Guidelines:
        - Answer the user's question clearly and concisely
        - If the question requires analysis, write python code using pandas ,matplotlib, or seaborn
        - For visualizarion always use plt.figure() before plotting and include plt.tight_layout()
        - Always validate data before operations (check for nulls,data types, etc..)
        - If you can't answer due to data limitations, explain why
        - Keep responsing focused on the data and questions asked
        - Summarize your findings, insights, and any relevant statistics or visual trends.
        - Focus on delivering the results and what they mean, not on how to get them.
        - If a chart or visualization would help, display the chart in the response using matplotlib or seaborn.
        - If a user asks for a specific visualization, display the chart in the response using matplotlib or seaborn.

        When writing code:
        - Import statements are already done (pandas as pd, matplotlib.pylot as plt, seaborn as sns)
        - The dataframe is available as 'df'
        - For plots, use plt.figure(figsize=(10,6)) for better display.
        - Always add titles and lables to plots
        """

        #Generate response
        with st.chat_message("assistant"):
            with st.spinner('Analyzing your data'):
                try:
                    response = client.chat.completions.create(
                        model= 'gpt-6-luna',
                        messages=[
                            {'role':'system','content':system_prompt},
                            {'role':'assistant','content':user_input}
                        ],
                        max_completion_tokens= 1500 #Ket qua duoi 1500 tu
                    )
                    reply=response.choices[0].message.content
                    st.markdown(reply)

                    #Save assistant response to history
                    st.session_state.messages.append({'role':'assistant','content':reply})

                except Exception as e:
                    st.error(f"Error generating response: {st(e)}")
                    st.info("Please try again or rephrase your question")


    else:
        #No data upload state:
        col1,col2,col3 = st.columns([1,2,1])
        with col2: 
            st.info('Please upload a csv file to start')
            #Example questions
            st.markdown('### Example questions you can ask: ')
            st.markdown("""
            - What are the main trends in my data?
            - Show me a correlation matrix 
            - Create a bar chart of the top 10 catergories
            - What's the average value by month ?
            - Are there any outliners in the price column?
            """)