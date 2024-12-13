import streamlit as st

def render_authentication_section():
    """Render the authentication section in the sidebar."""
    with st.sidebar.expander("Website Authentication", expanded=False):
        use_auth = st.checkbox("Enable Authentication")
        credentials = None
        
        if use_auth:
            st.session_state['username'] = st.text_input("Username/Email")
            st.session_state['password'] = st.text_input("Password", type="password")
            
            # Selectors for login form
            st.markdown("### Login Form Selectors")
            st.info("""
            Common selector examples:
            - ID: 'email', 'username', 'password'
            - Class: 'form-control', 'login-input'
            - XPath: '//button[@type="submit"]', '//input[@name="email"]'
            """)
            
            # Username field selector
            username_selector_type = st.selectbox(
                "Username Field Selector Type", 
                ["id", "class", "xpath"],
                index=0  # Default to 'id'
            )
            username_selector_value = st.text_input(
                "Username Field Selector",
                value="email" if username_selector_type == "id" else "",
                help="Example: 'email' for ID, 'form-control' for class"
            )
            st.session_state['username_field'] = {
                "type": username_selector_type,
                "value": username_selector_value
            }
            
            # Password field selector
            password_selector_type = st.selectbox(
                "Password Field Selector Type", 
                ["id", "class", "xpath"],
                index=0  # Default to 'id'
            )
            password_selector_value = st.text_input(
                "Password Field Selector",
                value="password" if password_selector_type == "id" else "",
                help="Example: 'password' for ID, 'form-control' for class"
            )
            st.session_state['password_field'] = {
                "type": password_selector_type,
                "value": password_selector_value
            }
            
            # Submit button selector
            submit_selector_type = st.selectbox(
                "Submit Button Selector Type", 
                ["id", "class", "xpath"],
                index=2  # Default to 'xpath'
            )
            submit_selector_value = st.text_input(
                "Submit Button Selector",
                value="//button[@type='submit']" if submit_selector_type == "xpath" else "",
                help="Example: '//button[@type=\"submit\"]' for XPath"
            )
            st.session_state['submit_button'] = {
                "type": submit_selector_type,
                "value": submit_selector_value
            }
            
            credentials = {
                "username_field": st.session_state['username_field'],
                "password_field": st.session_state['password_field'],
                "submit_button": st.session_state['submit_button'],
                "username": st.session_state['username'],
                "password": st.session_state['password']
            }
        
        return use_auth, credentials
