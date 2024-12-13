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
    if 'login_url' not in st.session_state:
        st.session_state['login_url'] = 'https://sigest.services/login'
    if 'username' not in st.session_state:
        st.session_state['username'] = ''
    if 'password' not in st.session_state:
        st.session_state['password'] = ''
    if 'username_field' not in st.session_state:
        st.session_state['username_field'] = {'type': 'id', 'value': 'email'}
    if 'password_field' not in st.session_state:
        st.session_state['password_field'] = {'type': 'id', 'value': 'password'}
    if 'submit_button' not in st.session_state:
        st.session_state['submit_button'] = {'type': 'xpath', 'value': "//button[@type='submit' and contains(@class, 'btn-dark')]"}
    if 'credentials' not in st.session_state:
        st.session_state['credentials'] = None
    
    # Cookie handling
    if 'cookie_selectors' not in st.session_state:
        st.session_state['cookie_selectors'] = []
    
    # Debug info
    print("Session state initialized with:")
    print("- scraping_state:", st.session_state.get('scraping_state'))
    print("- credentials:", st.session_state.get('credentials'))
    print("- username:", st.session_state.get('username'))
    print("- username_field:", st.session_state.get('username_field'))
    print("- password_field:", st.session_state.get('password_field'))
    print("- submit_button:", st.session_state.get('submit_button'))

def reset_session_state():
    """Reset session state to initial values."""
    st.session_state['scraping_state'] = 'idle'
    st.session_state['results'] = None
    st.session_state['credentials'] = None
    st.session_state['cookie_selectors'] = []
    
    # Clean up Selenium driver if it exists
    if st.session_state.get('driver'):
        try:
            st.session_state['driver'].quit()
        except:
            pass
        st.session_state['driver'] = None
    
    print("Session state reset")

def get_session_state():
    """Get current session state as a dictionary."""
    return {key: value for key, value in st.session_state.items()}
