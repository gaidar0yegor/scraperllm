import streamlit as st

def render_authentication_section():
    """Render the authentication section in the sidebar."""
    with st.sidebar.expander("Website Authentication", expanded=False):
        use_auth = st.checkbox("Enable Authentication", value=True)  # Default to enabled
        credentials = None
        
        if use_auth:
            # Login URL input
            login_url = st.text_input(
                "Login Page URL",
                value=st.session_state.get('login_url', 'https://sigest.services/login'),
                help="The URL of the login page"
            )
            st.session_state['login_url'] = login_url
            
            # Username/Email input
            username = st.text_input(
                "Username/Email",
                value=st.session_state.get('username', '2811.02@sigest.app'),  # Default value
                help="Enter your username or email"
            )
            st.session_state['username'] = username
            if not username:
                st.warning("Please enter your username/email")
            
            # Password input
            password = st.text_input(
                "Password",
                type="password",
                value=st.session_state.get('password', '2436$'),  # Default value
                help="Enter your password"
            )
            st.session_state['password'] = password
            if not password:
                st.warning("Please enter your password")
            
            # Selectors for login form
            st.markdown("### Login Form Selectors")
            st.info("""
            The login form uses the following fields:
            - Username field: id="email"
            - Password field: id="password"
            - Submit button: button[type='submit'] with class 'btn-dark'
            """)
            
            # Username field selector
            username_selector_type = "id"  # Fixed to use ID selector
            username_selector_value = "email"  # Fixed value from the form
            
            st.session_state['username_field'] = {
                "type": username_selector_type,
                "value": username_selector_value
            }
            
            # Password field selector
            password_selector_type = "id"  # Fixed to use ID selector
            password_selector_value = "password"  # Fixed value from the form
            
            st.session_state['password_field'] = {
                "type": password_selector_type,
                "value": password_selector_value
            }
            
            # Submit button selector
            submit_selector_type = "xpath"  # Fixed to use xpath selector
            submit_selector_value = "//button[@type='submit' and contains(@class, 'btn-dark')]"  # Fixed value from the form
            
            st.session_state['submit_button'] = {
                "type": submit_selector_type,
                "value": submit_selector_value
            }
            
            # Create credentials dictionary if username and password are provided
            if username and password:
                credentials = {
                    "login_url": login_url,
                    "username_field": st.session_state['username_field'],
                    "password_field": st.session_state['password_field'],
                    "submit_button": st.session_state['submit_button'],
                    "username": username,
                    "password": password
                }
                st.session_state['credentials'] = credentials  # Store in session state
                
                # Show debug information
                st.markdown("### Current Credentials")
                st.code(f"""
Login URL: {login_url}
Username: {username}
Username Field: id="{username_selector_value}"
Password Field: id="{password_selector_value}"
Submit Button: xpath="{submit_selector_value}"
""", language="text")
                
                # Debug print
                print("Credentials set:", credentials)
            else:
                st.error("Please enter your username and password")
                st.session_state['credentials'] = None  # Clear credentials
                print("Credentials cleared due to missing username/password")
        else:
            # Clear credentials if authentication is disabled
            st.session_state['credentials'] = None
            print("Credentials cleared - authentication disabled")
        
        return use_auth, credentials
