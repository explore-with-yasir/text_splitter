import os
from streamlit.web import cli as stcli

def app():
    # Set environment variable to run Streamlit in headless mode
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    stcli.main(['streamlit', 'run', 'splitter.py'])

if __name__ == "__main__":
    app()

