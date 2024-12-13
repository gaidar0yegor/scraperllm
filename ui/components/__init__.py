"""
Components package for the Universal Web Scraper UI.
This package contains all the UI components used in the main Streamlit application.
"""

from .api_keys import render_api_keys_section
from .authentication import render_authentication_section
from .cookie_handling import render_cookie_handling_section
from .scraping_settings import render_scraping_settings
from .scraping_logic import handle_scraping
from .results_display import display_scraping_results

__all__ = [
    'render_api_keys_section',
    'render_authentication_section',
    'render_cookie_handling_section',
    'render_scraping_settings',
    'handle_scraping',
    'display_scraping_results'
]
