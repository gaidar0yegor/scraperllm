import streamlit as st

def render_api_keys_section():
    """Render the API keys section in the sidebar."""
    with st.sidebar.expander("API Keys", expanded=False):
        st.session_state['openai_api_key'] = st.text_input(
            "OpenAI API Key",
            type="password"
        )
        st.session_state['gemini_api_key'] = st.text_input(
            "Gemini API Key",
            type="password"
        )
        st.session_state['groq_api_key'] = st.text_input(
            "Groq API Key",
            type="password"
        )
        st.session_state['ollama_url'] = st.text_input(
            "Ollama API URL (optional)", 
            value="",
            help="Leave empty to use local Ollama instance, or enter external Ollama API URL"
        )
        
        # Return all API keys as a dictionary
        return {
            'openai_api_key': st.session_state.get('openai_api_key', ''),
            'gemini_api_key': st.session_state.get('gemini_api_key', ''),
            'groq_api_key': st.session_state.get('groq_api_key', ''),
            'ollama_url': st.session_state.get('ollama_url', '')
        }
