"""
Universal Web Scraper UI Package.
This package contains all the UI components and utilities for the web scraper application.
"""

from .components import (
    render_api_keys_section,
    render_authentication_section,
    render_cookie_handling_section,
    render_scraping_settings,
    handle_scraping,
    display_scraping_results
)

from .utils import (
    init_session_state,
    reset_session_state,
    get_session_state
)

__version__ = '1.0.0'

__all__ = [
    'render_api_keys_section',
    'render_authentication_section',
    'render_cookie_handling_section',
    'render_scraping_settings',
    'handle_scraping',
    'display_scraping_results',
    'init_session_state',
    'reset_session_state',
    'get_session_state'
]
