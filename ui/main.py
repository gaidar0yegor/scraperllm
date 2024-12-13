import streamlit as st
import sys
import os

# Add project root to Python path to allow importing from project modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from selenium_utils import setup_selenium, handle_cookies, handle_login

# Import UI components using relative imports
from .components.api_keys import render_api_keys_section
from .components.authentication import render_authentication_section
from .components.cookie_handling import render_cookie_handling_section
from .components.scraping_settings import render_scraping_settings
from .components.scraping_logic import handle_scraping
from .components.results_display import display_scraping_results
from .utils.session_state import init_session_state

def main():
    """Main entry point for the Universal Web Scraper UI."""
    # Set up page configuration
    st.set_page_config(page_title="Universal Web Scraper", page_icon="🦑")
    st.title("Universal Web Scraper 🦑")

    # Initialize session state
    init_session_state()

    # Sidebar components
    st.sidebar.title("Web Scraper Settings")

    # Render all sidebar components
    api_keys = render_api_keys_section()
    use_auth, credentials = render_authentication_section()
    use_cookie_handling, cookie_selectors = render_cookie_handling_section()
    settings = render_scraping_settings()

    # Store credentials in session state if authentication is enabled
    if use_auth and credentials:
        st.session_state['credentials'] = credentials
    else:
        st.session_state['credentials'] = None

    # Store cookie selectors in session state
    if use_cookie_handling and cookie_selectors:
        st.session_state['cookie_selectors'] = cookie_selectors
    else:
        st.session_state['cookie_selectors'] = None

    # Main action button
    if st.sidebar.button("LAUNCH SCRAPER", type="primary"):
        if not settings['is_valid']:
            st.error(settings['error_message'])
        else:
            # Store settings in session state
            st.session_state['settings'] = settings
            st.session_state['scraping_state'] = 'waiting' if settings['attended_mode'] else 'scraping'
            st.rerun()

    # Handle scraping states
    if st.session_state['scraping_state'] == 'waiting':
        # Attended mode: set up driver and wait for user interaction
        if st.session_state['driver'] is None:
            st.session_state['driver'] = setup_selenium(attended_mode=True)
            
            # First handle login if enabled
            if st.session_state.get('credentials'):
                st.write("Attempting to log in...")
                login_success = handle_login(st.session_state['driver'], st.session_state['credentials'])
                if login_success:
                    st.success("Login successful!")
                else:
                    st.error("Login failed. Please check your credentials.")
                    st.session_state['driver'].quit()
                    st.session_state['driver'] = None
                    st.session_state['scraping_state'] = 'idle'
                    st.rerun()
            
            # Then navigate to the target URL
            st.session_state['driver'].get(settings['urls'][0])
            
            # Handle cookies if enabled
            if st.session_state.get('cookie_selectors'):
                handle_cookies(st.session_state['driver'], st.session_state['cookie_selectors'])
            
            st.write("Perform any required actions in the browser window that opened.")
            st.write("Navigate to the page you want to scrape.")
            st.write("When ready, click the 'Resume Scraping' button.")
        else:
            st.write("Browser window is already open. Perform your actions and click 'Resume Scraping'.")

        if st.button("Resume Scraping"):
            st.session_state['scraping_state'] = 'scraping'
            st.rerun()

    elif st.session_state['scraping_state'] == 'scraping':
        # Perform scraping
        try:
            results = handle_scraping(
                settings,
                st.session_state.get('credentials'),  # Use credentials from session state
                st.session_state.get('cookie_selectors')  # Use cookie selectors from session state
            )
            st.session_state['results'] = results
            st.session_state['scraping_state'] = 'completed'
            st.rerun()
        except Exception as e:
            st.error(f"Error during scraping: {str(e)}")
            if st.session_state.get('driver'):
                st.session_state['driver'].quit()
                st.session_state['driver'] = None
            st.session_state['scraping_state'] = 'idle'

    # Display results if available
    if st.session_state['scraping_state'] == 'completed' and st.session_state['results']:
        display_scraping_results(st.session_state['results'], settings['show_tags'])
        
        # Reset scraping state button
        if st.sidebar.button("Clear Results"):
            # Clean up
            if st.session_state.get('driver'):
                st.session_state['driver'].quit()
                st.session_state['driver'] = None
            st.session_state['scraping_state'] = 'idle'
            st.session_state['results'] = None
            st.session_state['credentials'] = None
            st.session_state['cookie_selectors'] = None
            st.rerun()
