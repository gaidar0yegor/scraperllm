"""
Utility functions for managing Streamlit session state.
"""

import streamlit as st

def init_session_state():
    """Initialize all required session state variables."""
    # Scraping state
    if 'scraping_state' not in st.session_state:
        st.session_state['scraping_state'] = 'idle'  # Possible states: 'idle', 'waiting', 'scraping', 'completed'
    
    # Results storage
    if 'results' not in st.session_state:
        st.session_state['results'] = None
    
    # Selenium driver
    if 'driver' not in st.session_state:
        st.session_state['driver'] = None
    
    # API Keys
    if 'openai_api_key' not in st.session_state:
        st.session_state['openai_api_key'] = ''
    if 'gemini_api_key' not in st.session_state:
        st.session_state['gemini_api_key'] = ''
    if 'groq_api_key' not in st.session_state:
        st.session_state['groq_api_key'] = ''
    if 'ollama_url' not in st.session_state:
        st.session_state['ollama_url'] = ''
    
    # Authentication
    if 'username' not in st.session_state:
        st.session_state['username'] = ''
    if 'password' not in st.session_state:
        st.session_state['password'] = ''
    if 'username_field' not in st.session_state:
        st.session_state['username_field'] = {'type': 'id', 'value': ''}
    if 'password_field' not in st.session_state:
        st.session_state['password_field'] = {'type': 'id', 'value': ''}
    if 'submit_button' not in st.session_state:
        st.session_state['submit_button'] = {'type': 'xpath', 'value': ''}
    
    # Cookie handling
    if 'cookie_selectors' not in st.session_state:
        st.session_state['cookie_selectors'] = []

def reset_session_state():
    """Reset session state to initial values."""
    st.session_state['scraping_state'] = 'idle'
    st.session_state['results'] = None
    
    # Clean up Selenium driver if it exists
    if st.session_state.get('driver'):
        try:
            st.session_state['driver'].quit()
        except:
            pass
        st.session_state['driver'] = None

def get_session_state():
    """Get current session state as a dictionary."""
    return {key: value for key, value in st.session_state.items()}
