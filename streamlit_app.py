# imports
import os, json, firebase_admin, streamlit as st, uuid, datetime
from constants import *
from pathlib import Path
from dotenv import load_dotenv
from firebase_admin import firestore
from firebase_admin import credentials
from langchain.prompts import load_prompt
from streamlit import session_state as ss
from langchain_openai import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import Chroma, FAISS
from langchain_core.prompts import PromptTemplate, load_prompt
from langchain_community.document_loaders import CSVLoader, PyPDFLoader

load_dotenv()  # load environment variables from .env file

# setting up file-paths
prompt = load_prompt(PROMPT_TEMPLATE)
CSV_DATA_SOURCE = CONFIG_DIR / "data" / "Nikhil.csv"
PDF_RESUME = CONFIG_DIR / "data" / "Nikhil_Nageshwar_Inturi_Resume_bioinformatics_master_bioinformatics.pdf"

# if CSV_DATA_SOURCE.exists() and PDF_RESUME.exists():
#     st.success("Data source and resume PDF found.")
# else:
#     st.error("Data source or resume PDF not found.")


# validate openai api key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    st.error("OpenAI API key not found in environment variables.")

# validate firebase credentials
b64_key = os.getenv(FIREBASE_SERVICE_ACCOUNT)
firebase_json_key = base64.b64decode(b64_key).decode()
firebase_credentials = json.loads(firebase_json_key)
# firebase_json_key_file = os.getenv("FIREBASE_JSON_KEY")
# if not firebase_json_key_file:
#     st.error("Firebase JSON key file not found in environment variables.")
# with open(firebase_json_key_file, "r", encoding="utf‑8") as f:
#     firebase_json_key = f.read()
# firebase_credentials = json.loads(firebase_json_key)

@st.cache_resource
def init_connection():
    """
    Initialize connection to Firebase Firestore using the firebase credentials
    """
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred)
    return firestore.client()

try:
    db = init_connection()  # Initialize connection to Firebase Firestore
except Exception as e:
    st.write("Failed to connect to Firebase:", e)

# Access Firebase Firestore collection
if 'db' in locals():
    conversations_collection = db.collection('nik_rag_bot_and_human_conversations')  # db collection in Firebase Firestore: nik_rag_bot_and_human_conversations
else:
    st.write("Unable to access conversations collection. Firebase connection not established.")

###############

# STREAMLIT APP
st.title("NikhilGPT - Nikhil's resume bot")
st.image("misc/nik.png", use_column_width=True)
with st.expander("Note:"):
    st.write("""This chatbot, powered by the GPT‑3.5‑turbo language model, is designed to answer questions about Nikhil’s professional background, publications, projects, and qualifications. Conversations are stored to help improve the quality of responses. Please keep inquiries respectful and avoid personal or inappropriate topics.""")

# Function to store conversation in Firebase
def store_conversation(conversation_id, user_message, bot_message, answered):
    """
    Store conversations in Firebase Firestore
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "conversation_id": conversation_id, "timestamp": timestamp,
        "user_message": user_message, "bot_message": bot_message,
        "answered": answered
    }
    conversations_collection.add(data)

embeddings = OpenAIEmbeddings()  # initialize OpenAI embeddings to generate embeddings from the csv/md/pdf documents

if os.path.exists(FAISS_INDEX_PATH):
    vectors = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
else:
    text_splitter = CharacterTextSplitter(separator="\n",chunk_size=400,chunk_overlap=40)
    pdf_loader = PyPDFLoader(PDF_RESUME)
    pdf_data = pdf_loader.load_and_split(text_splitter=text_splitter)
    csv_loader = CSVLoader(file_path=CSV_DATA_SOURCE, encoding="utf-8")
    csv_data = csv_loader.load()
    data = pdf_data + csv_data
    vectors = FAISS.from_documents(data, embeddings)  # embeddings are created and saved to FAISS index
    vectors.save_local(FAISS_INDEX_PATH)

# initialize conversational retrieval chain
retriever = vectors.as_retriever(search_type="similarity", search_kwargs={"k": 6, "include_metadata": True, "score_threshold": 0.6})
chain = ConversationalRetrievalChain.from_llm(llm=ChatOpenAI(temperature=TEMPERATURE, model_name=MODEL, openai_api_key=openai_api_key), 
                                              retriever=retriever, return_source_documents=True, verbose=True, chain_type="stuff",
                                              max_tokens_limit=4097, combine_docs_chain_kwargs={"prompt": prompt})

def is_valid_json(data):
    """
    Function to check if a string is a valid JSON
    """
    try:
        json.loads(data)
        return True
    except json.JSONDecodeError:
        return False

def conversational_chat(query):
    """
    Function to handle the conversation with the chatbot: gpt-3.5-turbo
    """
    with st.spinner("Thinking..."):
        result = chain({"system": "You are a Resume Bot, a comprehensive, interactive resource for exploring Nikhil's background, skills, and expertise. Be polite and provide answers based on the provided context only. Only answer questions relevant to Nikhil and his work experience. Answer question if there are ONLY regarding Nikhil. If the questions is not relevant to Nikhil, reply that you are a Resume bot. You can make up projects with the skills and projects I have if the question requests a skill set related to Bioinformatics, Neuroscience, Neuroinformatics, Generative AI, Machine Learning, Natural Language Processing, Software Development, Database management or Computer sciences.", 
                        "question": query, 
                        "chat_history": st.session_state['history']})
    if is_valid_json(result["answer"]):              
        data = json.loads(result["answer"])
    else:
        data = json.loads('{"answered":"false", "response":"Hmm... Something is not right. I\'m experiencing technical difficulties. Try asking your question again or ask another question about Nikhil\'s professional background and qualifications. Thank you for your understanding.", "questions":["What is Nikhil\'s professional experience?","What projects has Nikhil worked on?","What are Nikhil\'s career goals?"]}')
    
    answered = data.get("answered")
    response = data.get("response")
    questions = data.get("questions")
    full_response="--"
    
    st.session_state['history'].append((query, response))  # append user query and bot response to chat history
    
    if ('I am tuned to only answer questions' in response) or (response == ""):  # if the response is empty or the bot is not able to answer the question
        full_response = """Unfortunately, I can't answer this question. My capabilities are limited to providing information about Nikhil's professional background and qualifications. If you have other inquiries, I recommend reaching out to Nikhil on [LinkedIn](https://www.linkedin.com/in/nikhilinturi/). I can answer questions like: \n - What is Nikhil's educational background? \n - Can you list Nikhil's professional experience? \n - What skills does Nikhil possess? \n"""
        store_conversation(st.session_state["uuid"], query, full_response, answered)
    else: 
        markdown_list = ""
        for item in questions:
            markdown_list += f"- {item}\n"
        full_response = response + "\n\n What else would you like to know about Nikhil? You can ask me: \n" + markdown_list
        store_conversation(st.session_state["uuid"], query, full_response, answered)
    return(full_response)

if "uuid" not in st.session_state:
    st.session_state["uuid"] = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        welcome_message = """
            Welcome! I'm **Resume Bot**, a virtual assistant designed to provide insights into Nikhil's background and qualifications. 

            Feel free to inquire about any aspect of Nikhil's profile, such as his educational journey, internships, professional projects, areas of expertise in Data Science and AI, or his future goals.

                - His Master's in Machine Learning and AI from Purdue Global
                - His Master's in Business Analytics and AI from UTDallas
                - His experience at Infosys and Aganitha Cognitive Solutions
                - His proficiency in programming languages and ML/Generative AI frameworks
                - His experience in drug discovery and development
                - His expericnce and certifications on Cloud platforms
                - His passion for leveraging technologies to drive innovation

            What would you like to know first? I'm ready to answer your questions in detail.
            """
        message_placeholder.markdown(welcome_message)

if 'history' not in st.session_state:
    st.session_state['history'] = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me about Nikhil's background, projects, publications, etc..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        user_input=prompt
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        full_response = conversational_chat(user_input)
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})