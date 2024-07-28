import streamlit as st
from pathlib import Path
import streamlit_authenticator as stauth
from streamlit_extras.mention import mention
from streamlit_option_menu import option_menu
from langchain_chroma import Chroma
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.embeddings.ollama import OllamaEmbeddings
import os, time
import webbrowser
import random
from data import split_documents, add_to_db, get_embedding_function, delete_from_db
import base64
from pathlib import Path
import pickle
from datetime import datetime

port = 5000
BASE_PATH = Path(__file__).parent
# Define the path where the documents will be stored
DATA_PATH = os.path.join(BASE_PATH, 'docs')
CHROMA_DIR = os.path.join(BASE_PATH, 'db')
LOGO_PATH = os.path.join(BASE_PATH, 'images\images.png')
SAVED_PATH = os.path.join(BASE_PATH, 'saved_chats')
# Define the path where the Chroma database will be stored
# CHROMA_DIR = "D:/genAILLM/db"
# LOGO_PATH = "D:\genAILLM\images\images.png"
# SAVED_PATH = "D:/genAILLM/saved_chats/"


# Create the directory for uploading documents if it doesn't exist
if not os.path.exists(DATA_PATH):
    os.makedirs(DATA_PATH)

if not os.path.exists(SAVED_PATH):
    os.makedirs(SAVED_PATH)

db = Chroma(
    persist_directory=CHROMA_DIR,
    embedding_function=get_embedding_function()
)



# Template for creating the prompt that the AI will use to generate a response
PROMPT_TEMPLATE_RESPONSE = """
### Instructions:
You are an AI model designed to provide accurate and helpful responses based on the given context and chat history.
Please use the relevant documents from the vector store and the previous chat history to generate a response to the user's query. 
Do not give out citations. Restrict your responses to not more than one paragraph 70 to 80 words.

### Context:
{context}

### Chat History:
{chat_history}

### User Query:
{question}

### Response:
"""
PROMPT_TEMPLATE_QUERY = """
### Instructions:
You are an AI model designed to refine user queries based on the given context and chat history. 
Please use the relevant documents from the vector store and the previous chat history to understand 
the user's needs better and refine their query for improved clarity and specificity. 
Make sure while refining the actual essence of the user query should not get modified. 
You only have to return the refined query and DO NOT answer it. Keep the query consice and accurate.

### Context:
{context}

### Chat History:
{chat_history}

### Original User Query:
{question}

### Refined Query:
"""

# Initialize the Chroma database with a directory to persist data and the embedding function

def query_rag(query_text: str, chat_history, input_prompt_template):
    """
    Query the AI model with a given question and chat history.
    :param query_text: The question asked by the user.
    :param chat_history: The history of the chat session.
    :return: The AI's response text and sources of information.
    """
    # Search for the most relevant documents based on the query
    results = db.similarity_search_with_score(query_text, k=5)

    # Extract the content of the most relevant documents
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    
    # Format the prompt with the context and chat history
    prompt_template = ChatPromptTemplate.from_template(input_prompt_template)
    prompt = prompt_template.format(context=context_text, chat_history=chat_history, question=query_text)

    # Initialize the AI model
    model = Ollama(model="mistral", temperature=0.8)
    # Generate the response from the AI model
    response_text = model.invoke(prompt)
    # Extract sources of the information used in the response
    sources = [doc.metadata.get("id", None) for doc, _score in results]
    
    return response_text, sources


def save_new_document(uploaded_file):
    """
    Save the uploaded document to the defined directory.
    :param uploaded_file: The file uploaded by the user.
    """
    if uploaded_file is not None:
        # Save the uploaded file to the specified path
        file_path = os.path.join(DATA_PATH, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
    return None

def display_pdf(file_path):
    with open(file_path, "rb") as file:
        base64_pdf = base64.b64encode(file.read()).decode('utf-8')
        pdf_display = f"""
    <div style="border: 2px solid #000; padding: 5px; border-radius: 5px; width: 460px; margin: 0 auto; background-color: black;">
        <embed src="data:application/pdf;base64,{base64_pdf}" width="450" height="300" type="application/pdf">
    </div>
    """
        st.markdown(pdf_display, unsafe_allow_html=True)

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded


def img_to_html(img_path):
    img_html = "<div style='display: flex; justify-content: center; align-items: center; height: 20vh; border: 1px solid white; background-color: white; margin-bottom: 10px; border-radius: 50%'><img src='data:image/png;base64,{}'alt='Centered Image' style='max-width: 80%; max-height: 80%;'></div>".format(img_to_bytes(img_path))
    return img_html

def refresh_page(count:int=1):
    count = count
    while count >= 0:
        st.experimental_rerun()
        count -= 1

# Initialize chat history if it doesn't exist in the session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Set the page config
st.set_page_config(page_title="CHAT APP", layout="wide")
@st.cache_data
def get_base64_of_img(image):
    with open(image, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

img_bg = get_base64_of_img("images/chat-bg1.jpg")
img_side = get_base64_of_img("images/bg.jpg")

page_bg_image=f"""
<style>
[data-testid="stApp"] {{
    background-image: url("data:image/png;base64,{img_bg}");
    background-size: stretch;
}}

[data-testid="stHeader"] {{
    background-color: rgba(0, 0, 0, 0);
}}

[data-testid="stToolbar"] {{
    color: rgba(0, 0, 0, 0);
}}

[data-testid="stSidebar"] {{
    background-image: url("data:image/png;base64,{img_side}");
}}
</style>
"""
st.markdown(page_bg_image, unsafe_allow_html=True)

with st.sidebar:
    tab = option_menu(
    menu_title="",
    # menu_icon='chat-text-fill',
    options=["Chat", "Admin", "About"],
    icons=["chat", "gear", "info-circle"],
    default_index=0,
    orientation='horizontal'
)
    st.markdown(img_to_html(LOGO_PATH), unsafe_allow_html=True)
    option_menu(
        menu_title=f"Query Count: {len(st.session_state.chat_history)}",
        menu_icon="memory",
        options = [chat['user'] for chat in st.session_state.chat_history] if len(st.session_state.chat_history) > 0 else ["No previous queries"]
    )

    help_clear_chat = """
            Deletes previous chat history so the AI does not use your previous chats
            to build context to answer next query. Use incase you want to chage the 
            topic of chat and start afresh
            """
    if st.button(label="Clear Chat", use_container_width=True, disabled=False if len(st.session_state.chat_history) > 0 else True, help=help_clear_chat):
        st.session_state.chat_history.clear()
        st.toast(body=f"Chat history cleared", icon="🚨")

    help_export_chat = """
            Exports and saves your chats in a JSON format. 
            They can be retrieved later or be used for analysis.
            """
    if st.button(label="Save & Export Chat", use_container_width=True, disabled=False if len(st.session_state.chat_history) > 0 else True, help=help_export_chat):
        
        filename = "".join(ch for ch in str(st.session_state.chat_history[0]['user']) if ch.isalnum())+ datetime.now().strftime("%Y-%m-%d-%H-%M") + ".pkl"
        try:
            if not os.path.exists(SAVED_PATH):
                os.mkdir(SAVED_PATH)

            with open(SAVED_PATH + filename, 'wb') as file:
                pickle.dump(st.session_state.chat_history, file)
            st.toast(body=f"Chat saved as {filename}")
        except Exception as e:
            st.error(f"Error: {e}")
    
    help_load_chat = """
            Load your previously saved chats 
            to build chat context
            """
    if len(st.session_state.chat_history) == 0:
        filenames = st.multiselect(
            label="Load Chat",
            options=[".".join(filename.split(".")[:-1]) for filename in os.listdir(SAVED_PATH) if filename.endswith('pkl')],
            placeholder="Choose a chat to load"
        )
        if st.button(label="Load Chat History", use_container_width=True, disabled=True if len(os.listdir(SAVED_PATH)) == 0 else False, help=help_load_chat):
            # Dropdown to select the chat file
            
            # if len(filenames) >0 :
            for filename in filenames:
                if filename != '':
                    try:
                        filename = str(filename) + '.pkl'
                        with open(os.path.join(SAVED_PATH, filename), 'rb') as file:
                            chats = pickle.load(file)
                        
                        keys = [key['key'] for key in st.session_state.chat_history]
                        for chat in chats:
                            if chat['key'] not in keys:
                                st.session_state.chat_history.append(chat)
                                st.toast(body="Chat history loaded in session")
                            else:
                                st.toast(body="Chat already loaded")
                    except Exception as e:
                        st.error(f"Error: {e}")

    
# Tab1: Chat Space
if tab == "Chat":
    # Set the title of the Streamlit app
    st.markdown("<h1 style='text-align: center;'><span style='font-size: 80px; color: red'>AI</span><span style='text-align: center; color: black'>Powered Search 🦉📄</span></h1>", unsafe_allow_html=True)
    # Add a caption and markdown description about the app
    st.markdown("<p style='text-align: center;'><span style='text-align: center; color: black;'>This is a Generative AI powered Question and Answer app that responds to questions about your PDF files.</span></p>", unsafe_allow_html=True)
    
    # Input widget for the user to ask questions
    prompt = st.chat_input("Your question here...")
    st.markdown("""
    <style> 
    .stBottom {
    background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)
   
    if prompt:
        # Refine User Query
        refined_query, _ = query_rag(prompt, chat_history=st.session_state.chat_history, input_prompt_template=PROMPT_TEMPLATE_QUERY)
        # Get the AI's response and sources based on the user's question and chat history
        answer, metadata = query_rag(refined_query, chat_history=st.session_state.chat_history, input_prompt_template=PROMPT_TEMPLATE_RESPONSE)
        # Add the user's question and AI's response to the chat history
        st.session_state.chat_history.append({"user": prompt, "user_refined":refined_query, "response": answer, "metadata":metadata, "key":random.randint(1, 999999), "feedback":""})
        # Keep only the last 5 chat interactions
        if len(st.session_state.chat_history) > 5:
            st.session_state.chat_history.pop(0)

    # Display the chat history in the app
    
    if st.session_state.chat_history:
        
        for chat in st.session_state.chat_history:
            st.chat_message("user").markdown(chat['user'])
            st.info(f"Refined Query:  {chat['user_refined']}")
            st.chat_message("assistant").markdown(chat['response'])
            key = chat['key']
            labels = {}       
            # This code can be used to display source metadata
            for source in chat['metadata']:
                
                source =  source.split(":")
                document = source[0]+":"+source[1]
                page = source[2]
                chunk = source[-1]
                path = document + "#page=" + page
                
                label = document.split(":")[-1].split("/")[-1]+", Page No: "+ page
                labels[label]= path
                
            
            # st.write([(labels[label], label) for label in labels.keys()])
            colList = st.columns(3, gap='medium', vertical_alignment="center")

            for i, label in enumerate(labels.keys()):
                with colList[i%3]: 
                    path = str(labels[label])
                    mention(label=label, url=path)
                           

                    
# Tab2: Admin Panel
elif tab == "Admin":

    config = {'credentials': {'usernames': {'admin': {'email': 'admin@mail.in', 'name': 'admin', 'password': 'admin123'}}, 'cookie': {'expiry_days': 1, 'key': 'mycookiekeyisveryrandom', 'name': 'authcookieadmin'}}}

    authenticator = stauth.Authenticate(
        config['credentials'],
        'authcookieadmin',
        'mycookiekeyisveryrandom',
        1,
    )

    authenticator.login()
    
    if st.session_state['authentication_status'] == False:
        st.error("Username/Password is incorrect")

    if st.session_state['authentication_status'] == None:
        st.warning("Please enter username and password")
    
    if st.session_state['authentication_status']:
        # if st.session_state['name']=='admin':
        #     # st.session_state.show_logout = True

        col1, col2 = st.columns(2, gap='medium', vertical_alignment='center')

        with col2:
            sources = []
            for x in range(len(db.get()["ids"])):
                doc = db.get()["metadatas"][x]
                sources.append(doc['source'])
            selected_doc = option_menu(
                menu_title=f"Ingested Documents: {len(set(sources))}",
                menu_icon='book',
                options=[doc.split('/')[-1] for doc in set(sources)],
                icons=['page' for i in range(len(set(sources)))],
                default_index=0,
                # orientation='horizontal'
            )
            # selected_doc = st.multiselect(
            #     label='',
            #     options=[doc.split('/')[-1] for doc in set(sources)],
            #     placeholder="Select the Documents to be removed from Database",
            # )
            # Check if user is still authenticated
            if 'name' in st.session_state and 'authentication_status' in st.session_state:
                if st.session_state['authentication_status']:
                    if st.button(label="Delete Documents", key='delete_docs', disabled=False if selected_doc else True):
                        
                        docs_to_delete = [selected_doc]
                        # for i in range(len(selected_doc)):
                        #     docs_to_delete.append(selected_doc[i])
                        
                        status, return_val = delete_from_db(docs_to_delete)
                            
                        if status == True:
                            st.toast(f":red[{selected_doc} file (s) deleted from the database...]", icon=":material/warning:")
                            # st.rerun()
                        else:
                            st.error(return_val['error'])
                        
                else:
                    st.toast(":red[Please login before proceeding...]")
            else:
                st.toast(":red[Please login before proceeding...]")
        
        with col1:
            st.markdown("<h4 style='text-align: Left;'><span style='font-size: 40px; color: red'>Admin</span><span style='font-size:15px; color:grey;'>  Configure  settings here</span></h4>", unsafe_allow_html=True)
            # File uploader widget to upload PDF documents
            if "uploader_key" not in st.session_state:
                st.session_state.uploader_key = 0
            def update_uploader_key():
                st.session_state.uploader_key += 1
            uploaded_files = st.file_uploader("Choose a file", type=["pdf"], key= f"uploader_{st.session_state.uploader_key}", accept_multiple_files=True, label_visibility="collapsed")

            if selected_doc:
                st.write("### PDF Preview")
                display_pdf(DATA_PATH + selected_doc)
            if uploaded_files:
                # st.session_state.show_logout = False
                for uploaded_file in uploaded_files:
                    save_new_document(uploaded_file=uploaded_file)

                    
                    # Button to process the uploaded document
                    with st.status(f"Uploading {uploaded_file.name}", expanded=True) as status:
                        st.write(f"{uploaded_file.name} uploaded")
                        texts = split_documents(chunk_size=1000, chunk_overlap=200, path=DATA_PATH, file=str(uploaded_file.name))
                        st.write(f"{uploaded_file.name} chunked and vectorised")
                        # Add the text chunks to the database
                        new_texts, existing_ids = add_to_db(texts=texts)
                        st.write(f"{len(existing_ids)} vectors existing in database")
                        time.sleep(2)
                        status.update(label=f"{len(new_texts)} new vectors added to the database successfully", state="complete", expanded=False)

                        # st.rerun() 
                # st.session_state.show_logout = True
      

        
                
              
    if st.session_state['name'] == 'admin':
        authenticator.logout("Logout", "sidebar")     
  
# Tab3: About Us
elif tab == "About":
    st.title("About Us")
    st.write("This is the About Us section of the app.")
    st.markdown("""
    ### About Our App
    This app is a demonstration of a multi-tab interface using Streamlit.
    
    ### Contact
    For more information, contact us at [email@example.com](mailto:email@example.com)
    """)

