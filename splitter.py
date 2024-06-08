import streamlit as st
import re
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter, Language
import tiktoken
import docx

# Initialize token encoder
enc = tiktoken.get_encoding("cl100k_base")

# Splitter and language options
splitters = [
    'Split code',
    'CharacterTextSplitter',
    'RecursivelyCharacterTextSplitting',
    'Split by tokens (OpenAI)'
]

languages = ['CPP', 'GO', 'JAVA', 'JS', 'PHP', 'PROTO', 'PYTHON', 'RST', 'RUBY', 'RUST', 'SCALA', 'SWIFT', 'MARKDOWN', 'LATEX', 'HTML', 'SOL']

files_types = [
    {"extension": "txt", "language": "MARKDOWN"},
    {"extension": "docx", "language": "DOCUMENT"},
    {"extension": "py", "language": "PYTHON"},
    {"extension": "php", "language": "PHP"},
    {"extension": "html", "language": "HTML"},
    {"extension": "js", "language": "JS"},
    {"extension": "css", "language": "CSS"},
    {"extension": "md", "language": "MARKDOWN"}
]

# Initialize session state
for key in ['file_extension', 'file_language', 'tokenized_content']:
    if key not in st.session_state:
        st.session_state[key] = ''

def file_upload():
    """Handles file upload and sets the file extension and language in session state."""
    uploaded_file = st.sidebar.file_uploader("Drop a file here or click to upload", type=[file["extension"] for file in files_types])
    if uploaded_file:
        st.session_state['file_extension'] = uploaded_file.name.split(".")[-1]
        st.session_state['file_language'] = next((file["language"].lower() for file in files_types if file["extension"] == st.session_state['file_extension']), '')
        return uploaded_file
    return None

def display_metrics(chunks, tokens, characters):
    """Displays key performance indicators."""
    col1, col2, col3 = st.columns(3)
    token_ratio = round(tokens / st.session_state['tokenized_content'], 2)
    col1.metric("Total Characters", characters)
    col2.metric("Total Tokens", tokens, token_ratio, delta_color="inverse" if token_ratio != 1 else "off")
    col3.metric("Total Chunks", chunks)
    
   

def read_docx_file(uploaded_file):
    doc = docx.Document(uploaded_file)
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text

def create_dataframe(text_splitter, file_content):
    """Creates and displays a dataframe with chunked content."""
    chunks = text_splitter.create_documents([file_content])
    st.session_state['tokenized_content'] = len(enc.encode(file_content))
    df = pd.DataFrame({
        "Text": [chunk.page_content for chunk in chunks],
        "Tokens (Count)": [len(enc.encode(chunk.page_content)) for chunk in chunks],
        "Characters (Count)": [len(chunk.page_content) for chunk in chunks]
    })
    display_metrics(len(df), df['Tokens (Count)'].sum(), df['Characters (Count)'].sum())
    if df.empty:
        st.error('No content found.')
    else:
        st.dataframe(df, use_container_width=True)

# Streamlit app configuration
st.set_page_config(
    page_title="Splitter",
    page_icon="✂️✂️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.yasirsiddique.com/help',
        'Report a bug': "https://www.yasirsiddique.com/bug",
        'About': "# Visualize your text splitting algorithm!"
    }
)

st.title("✂️ Splitter ✂️")
st.markdown("#### Visualize how different text splitter algorithms and chunk sizes split/chunk code and text files.")
st.divider()

# File upload and processing
uploaded_file = file_upload()

if uploaded_file:
    file_content = None
    if st.session_state['file_extension'] == 'docx':
        file_content = read_docx_file(uploaded_file)
    else:
        file_content = uploaded_file.getvalue().decode("utf-8")

    if file_content:
        splitter = st.sidebar.selectbox('Select a splitter', splitters, index=1 if st.session_state['file_extension'] == "txt" or st.session_state['file_extension'] == "docx" else 0)
        chunk_size = st.sidebar.slider('Chunk Size', 1, 500, 1000)
        chunk_overlap = st.sidebar.slider('Overlap', 0, chunk_size, 0)

        splitter_index = splitters.index(splitter)
        
        if splitter_index == 0:
            language_selector = st.sidebar.selectbox('Select a language', languages, index=languages.index(st.session_state['file_language'].upper()))
            text_splitter = RecursiveCharacterTextSplitter.from_language(
                language=Language[language_selector],
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
        elif splitter_index == 1:
            text_splitter_separator = st.sidebar.text_input('Separator', value="\n\n", help="Specify the character separator", placeholder="Enter a separator like \\n\\n", max_chars=10)
            text_splitter_separator = re.sub(r'\\', '', text_splitter_separator)
            text_splitter = CharacterTextSplitter(
                separator=text_splitter_separator,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
        elif splitter_index == 2:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
        else:
            text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
        
        create_dataframe(text_splitter, file_content)

        if uploaded_file is not None:
            with st.expander(f"View Original File {uploaded_file.name} – {st.session_state['file_language']}"):
                st.code(file_content, language=st.session_state['file_language'], line_numbers=True)


#Credits
st.sidebar.markdown("This project was created by [Yasir Siddique](https://github.com/explore-with-yasir) [Linkedin](https://linkedin.com/in/yasir-sd).")
