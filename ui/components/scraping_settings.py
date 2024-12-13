import streamlit as st
from streamlit_tags import st_tags_sidebar
import sys
import os

# Add project root to Python path to allow importing from assets
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from assets import PRICING

def render_scraping_settings():
    """Render the main scraping settings in the sidebar."""
    # Model selection
    model_options = ["Ollama"] + [k for k in PRICING.keys() if k != "Ollama"]  # Put Ollama first
    model_selection = st.sidebar.selectbox("Select Model", options=model_options, index=0)

    # URL input with default value
    default_url = "https://weboutilmag.sigest.services/shop-product-prices/management"
    url_input = st.sidebar.text_input(
        "Enter URL(s) separated by whitespace",
        value=default_url,
        help="The URL to scrape after login"
    )
    urls = url_input.strip().split()
    num_urls = len(urls)

    # Fields to extract
    show_tags = st.sidebar.toggle("Enable Scraping", value=True)  # Default to enabled
    fields = []
    if show_tags:
        default_fields = ["title", "price", "status"]  # Default fields
        fields = st_tags_sidebar(
            label='Enter Fields to Extract:',
            text='Press enter to add a field',
            value=default_fields,  # Set default fields
            suggestions=default_fields,
            maxtags=-1,
            key='fields_input'
        )

    st.sidebar.markdown("---")

    # Pagination and Attended Mode options
    use_pagination = False
    attended_mode = False
    pagination_details = ""

    if num_urls <= 1:
        # Pagination settings
        use_pagination = st.sidebar.toggle("Enable Pagination")
        if use_pagination:
            pagination_details = st.sidebar.text_input(
                "Enter Pagination Details (optional)",
                help="Describe how to navigate through pages (e.g., 'Next' button class, URL pattern)"
            )

        st.sidebar.markdown("---")

        # Attended mode toggle
        attended_mode = st.sidebar.toggle("Enable Attended Mode")
        if attended_mode:
            st.sidebar.info("""
            Attended Mode enabled:
            1. Browser will open and log in
            2. You can verify the login
            3. Click 'Resume Scraping' when ready
            """)
    else:
        # Multiple URLs entered; disable Pagination and Attended Mode
        st.sidebar.info("Pagination and Attended Mode are disabled when multiple URLs are entered.")

    st.sidebar.markdown("---")

    # Store settings in session state
    if 'settings' not in st.session_state:
        st.session_state['settings'] = {}
    
    st.session_state['settings'].update({
        'model_selection': model_selection,
        'urls': urls,
        'show_tags': show_tags,
        'fields': fields,
        'use_pagination': use_pagination,
        'pagination_details': pagination_details,
        'attended_mode': attended_mode
    })

    # Validate inputs
    is_valid = True
    error_message = None

    if url_input.strip() == "":
        is_valid = False
        error_message = "Please enter at least one URL."
    elif show_tags and len(fields) == 0:
        is_valid = False
        error_message = "Please enter at least one field to extract."

    # Return all settings as a dictionary
    return {
        'model_selection': model_selection,
        'urls': urls,
        'show_tags': show_tags,
        'fields': fields,
        'use_pagination': use_pagination,
        'pagination_details': pagination_details,
        'attended_mode': attended_mode,
        'is_valid': is_valid,
        'error_message': error_message
    }
