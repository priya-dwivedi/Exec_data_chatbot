import openai
import time
import streamlit as st
from assistants_helper import *
from dashboard_utils import *
import base64
from PIL import Image

def main():
    st.sidebar.title('Navigation')
    page_options = ['Dashboard', 'Chatbot']
    selected_page = st.sidebar.selectbox('Select Page', page_options)

    if 'Dashboard' in selected_page:
        dashboard()
    if 'Chatbot' in selected_page:
        chatbot()


def dashboard():
    st.title(" :bar_chart: Sample Dashboard")
    st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)
    st.write("**This will be your customizable dashboard.**")

    ## Plot 1 - Top 7 companies with the largest asset size
    # Create a filter for countries
    allowed_countries = ['USA', 'China', 'Japan', 'Germany', 'France', 'Britain', 'South Korea', 'Netherlands', 'Switzerland', 'Canada']
    with st.expander("Filter"):
        selected_countries = st.multiselect("Pick your Country or leave blank", allowed_countries)

    fig = biggest_assets(selected_countries)
    st.plotly_chart(fig,use_container_width=True, height = 200)

    st.divider()

    ### Current Rank and Previous Rank of top 10 companies
    fig = rank_comparison()
    st.plotly_chart(fig,use_container_width=True, height = 200)

    st.divider()

    ### Geo plotting 
    allowed_params= ['Assets($millions)', 'Number of Employees', 'Revenues($millions)', 'Profits($millions)']
    # Add the radio buttons
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: center;} </style>', unsafe_allow_html=True)

    st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>', unsafe_allow_html=True)

    selected_metric = st.radio("Select your metric:", allowed_params, key="radio", index=1, format_func=lambda x: x)
    fig = plot_geo_locs(selected_metric)
    st.plotly_chart(fig,use_container_width=True, height = 200)


def chatbot():
    st.title("Chat-with-your-financials")
    st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

    img = Image.open('./logo1.png')
    img_resized = img.resize((200,200))
    st.image(img_resized)
    st.write("**Welcome to chat with your financials. This is a chatbot that can help you with your financial queries.**")
    # Writing a portion of the text in a different color
    st.markdown("You can ask questions like <span style='color: green;'>Show me the top 5 companies with the highest assets</span>", unsafe_allow_html=True)
    # st.write("You can ask questions like 'Show me the top 5 companies with the highest assets'")

    if 'client' not in st.session_state:
        # Initialize the client
        st.session_state.client = openai.OpenAI()
        st.session_state.assistant_id = 'asst_kEUFI9XjWRWqD6jMlvIfkIXi'
        # st.session_state.file = st.session_state.client.files.create(
        #     file=open("songs.txt", "rb"),
        #     purpose='assistants'
        # )

        # # Step 1: Create an Assistant
        # st.session_state.assistant = st.session_state.client.beta.assistants.create(
        #     name="Customer Service Assistant",
        #     instructions="You are a customer support chatbot. Use your knowledge base to best respond to customer queries.",
        #     model="gpt-4-1106-preview",
        #     file_ids=[st.session_state.file.id],
        #     tools=[{"type": "retrieval"}]
        # )

        # Step 2: Create a Thread
        st.session_state.thread = st.session_state.client.beta.threads.create()

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Type your question here."):
        ## Add user message to message thread for OpenAI
        # Step 3: Add a Message to a Thread
        message = st.session_state.client.beta.threads.messages.create(
            thread_id=st.session_state.thread.id,
            role="user",
            content=prompt
        )
        ## Step 4: Start the run
        run = st.session_state.client.beta.threads.runs.create(
            thread_id=st.session_state.thread.id,
            assistant_id=st.session_state.assistant_id,
            instructions="When plotting charts please include titles and axis names to make them neat. Also keep changing the colors of the plots"
        )

        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        while True:
            # Wait for 1 seconds
            time.sleep(1)

            # Retrieve the run status
            run_status = st.session_state.client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread.id,
                run_id=run.id
            )

            # If run is completed, get messages
            if run_status.status == 'completed':
                message_list, filename = query_completed_run(st.session_state.thread.id)
                for message in message_list:
                    with st.chat_message("assistant"):
                        st.markdown(message)
                        st.session_state.messages.append({"role": "assistant", "content": message})
                if filename is not None:
                    image_data = load_fig_from_openai(filename)
                    with st.chat_message("assistant"):
                        st.image(base64.b64decode(image_data), use_column_width=True)
                        # st.session_state.messages.append({"role": "assistant", "content": st.image(base64.b64decode(image_data), use_column_width=True)})


                break
            else:
                st.write("Assistant is working on your question...")
                time.sleep(10)
       

if __name__ == "__main__":
    main()