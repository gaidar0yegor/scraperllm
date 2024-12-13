import streamlit as st

def render_cookie_handling_section():
    """Render the cookie handling section in the sidebar."""
    with st.sidebar.expander("Cookie Popup Handling", expanded=False):
        use_cookie_handling = st.checkbox("Enable Cookie Popup Handling")
        cookie_selectors = None
        
        if use_cookie_handling:
            st.markdown("### Cookie Button Selectors")
            st.info("""
            Common selector examples:
            - ID: 'accept-cookies', 'cookie-consent', 'cookie-accept'
            - Class: 'accept-button', 'cookie-btn', 'consent-accept'
            - XPath: '//button[contains(text(), "Accept")]', '//button[@aria-label="Accept cookies"]'
            """)
            
            cookie_selectors = []
            num_selectors = st.number_input("Number of selectors", min_value=1, value=1)
            
            for i in range(num_selectors):
                st.markdown(f"#### Selector {i+1}")
                selector_type = st.selectbox(
                    "Type", 
                    ["id", "class", "xpath"],
                    key=f"cookie_selector_type_{i}"
                )
                selector_value = st.text_input(
                    "Value",
                    key=f"cookie_selector_value_{i}",
                    help="Enter selector value based on the type selected"
                )
                if selector_value:
                    cookie_selectors.append({
                        "type": selector_type,
                        "value": selector_value
                    })
        
        return use_cookie_handling, cookie_selectors
