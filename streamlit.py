import openai
import time
import streamlit as st
from assistants_helper import *
import base64
from PIL import Image


def main():
    st.title("Cha(r)t-with-your-CSV")
    st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

    img = Image.open('./friendly_bot.png')
    img_resized = img.resize((200,200))
    st.image(img_resized)
    st.write("**Welcome to chat with your CSV.**")
    # Writing a portion of the text in a different color
    st.markdown("You can ask questions like <span style='color: green;'>Show me the top 5 companies with the highest assets</span>", unsafe_allow_html=True)
    # st.write("You can ask questions like 'Show me the top 5 companies with the highest assets'")

    ## Ask user to upload a file
    # File uploader
    uploaded_file = st.file_uploader("Upload a file", type=["csv", "txt"])
    if uploaded_file is not None:

        if 'client' not in st.session_state:
            # Initialize the client
            st.session_state.client = openai.OpenAI()
            st.session_state.file = st.session_state.client.files.create(
                file=uploaded_file,
                purpose='assistants'
            )

            system_prompt = '''
                    You are a data analyst specializing in extracting insights from CSVs from using pandas and then visualizing it. 
                    You listen attentively to the customer and extract data for them. 
                    You show raw data as markdown table when possible and plot it. You also give a brief summary of the observed trend.
                    '''
            # Step 1: Create an Assistant
            st.session_state.assistant = st.session_state.client.beta.assistants.create(
                name="Data Visualization Assistant",
                instructions=system_prompt,
                model="gpt-4-1106-preview",
                file_ids=[st.session_state.file.id],
                tools=[{"type": "code_interpreter"}]
            )

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
                assistant_id=st.session_state.assistant.id,
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