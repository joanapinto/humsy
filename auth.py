"""
Authentication module for Humsy beta access
This module provides shared authentication logic for all pages
"""

import streamlit as st
import json
import os
from pathlib import Path

# Load allowed emails from Streamlit secrets
def load_whitelist():
    """Load the list of allowed email addresses from Streamlit secrets"""
    try:
        # Get allowed emails from Streamlit secrets
        allowed_emails = st.secrets.get("allowed_emails", [])
        
        # Ensure it's a list and convert to lowercase
        if isinstance(allowed_emails, str):
            # If it's a single string, split by comma or newline
            allowed_emails = [email.strip().lower() for email in allowed_emails.replace('\n', ',').split(',') if email.strip()]
        elif isinstance(allowed_emails, list):
            # If it's already a list, convert to lowercase
            allowed_emails = [email.strip().lower() for email in allowed_emails if email.strip()]
        else:
            # If it's not a string or list, return empty list
            allowed_emails = []
        
        return allowed_emails
    except Exception:
        # If secrets are not configured or there's an error, return empty list (no access)
        return []

def get_admin_email():
    """Get the admin email from Streamlit secrets"""
    try:
        # First try to get admin_email from secrets
        admin_email = st.secrets.get("admin_email", "")
        if admin_email:
            return admin_email.strip().lower()
        
        # Fallback: use the first email in allowed_emails as admin
        allowed_emails = load_whitelist()
        if allowed_emails:
            return allowed_emails[0]
        
        # Final fallback for development
        return "joanapnpinto@gmail.com"
    except Exception:
        # Fallback for development
        return "joanapnpinto@gmail.com"

def save_user_session(email: str, remember_me: bool = False):
    """Save user session data"""
    session_data = {
        "email": email,
        "remember_me": remember_me,
        "timestamp": st.session_state.get("session_timestamp", None)
    }
    
    # Save to session state
    st.session_state.user_email = email
    st.session_state.remember_me = remember_me
    
    # If remember me is enabled, save to file
    if remember_me:
        try:
            with open("data/user_session.json", "w") as f:
                json.dump(session_data, f)
        except Exception:
            pass  # Silently fail if we can't save

def load_user_session():
    """Load user session data from file"""
    try:
        if os.path.exists("data/user_session.json"):
            with open("data/user_session.json", "r") as f:
                session_data = json.load(f)
                
            # Check if remember me was enabled
            if session_data.get("remember_me", False):
                return session_data.get("email")
    except Exception:
        pass  # Silently fail if we can't load
    
    return None

def check_beta_access():
    """
    Check if the current user has beta access.
    Returns True if authorized, False otherwise.
    """
    allowed_emails = load_whitelist()
    
    # Check if user is logged in via session state
    if "user_email" in st.session_state and st.session_state.user_email is not None:
        return st.session_state.user_email.lower() in allowed_emails
    
    # Check if user has saved session
    saved_email = load_user_session()
    if saved_email and saved_email.lower() in allowed_emails:
        st.session_state.user_email = saved_email
        return True
    
    return False

def require_beta_access():
    """
    Require beta access for the current page.
    If user is not authorized, show login form and stop execution.
    """
    if not check_beta_access():
        # Clear any existing content
        st.empty()
        
        # Show login form
        st.title("🔐 Beta Access Required")
        st.write("This page requires beta access. Please enter your email:")
        
        # Pre-fill with saved email if available
        saved_email = load_user_session()
        email_input = st.text_input("Email", value=saved_email or "", key="beta_email_input")
        
        # Remember me checkbox
        remember_me = st.checkbox("Remember my email", value=bool(saved_email), key="remember_me_checkbox")
        
        if st.button("Continue", key="beta_continue_btn"):
            allowed_emails = load_whitelist()
            if email_input.strip().lower() in allowed_emails:
                # Save user session
                save_user_session(email_input.strip().lower(), remember_me)
                st.success("✅ Access granted. Welcome!")
                st.rerun()
            else:
                st.error("❌ Sorry, this email is not on the beta access list.")
        
        # Show helpful message
        st.info("💡 If you believe you should have access, please contact the administrator.")
        
        # iOS 16 compatibility check
        ios16_notice = """
        <div id="ios16-notice" style="display: none; position: fixed; top: 0; left: 0; right: 0; background: #ff6b6b; color: white; padding: 20px; text-align: center; z-index: 9999; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="max-width: 600px; margin: 0 auto;">
                <h2 style="margin: 0 0 15px 0; font-size: 24px;">📱 iOS 16 Compatibility Issue</h2>
                <p style="margin: 0 0 15px 0; font-size: 16px; line-height: 1.5;">
                    <strong>This app doesn't work on iPhone with iOS 16</strong> due to a known Safari compatibility issue.
                </p>
                <p style="margin: 0 0 20px 0; font-size: 14px; line-height: 1.4;">
                    <strong>To use this app, please:</strong><br>
                    • Update your iPhone to iOS 17 or later, OR<br>
                    • Use a computer with Chrome, Firefox, or Safari 17+
                </p>
                <p style="margin: 0; font-size: 12px; opacity: 0.8;">
                    This is a known issue with iOS 16 Safari and Streamlit apps.
                </p>
            </div>
        </div>

        <script>
        // Detect iOS 16 specifically
        function isIOS16() {
            const userAgent = navigator.userAgent;
            const isIOS = /iPad|iPhone|iPod/.test(userAgent);
            const isSafari = /Safari/.test(userAgent) && !/Chrome/.test(userAgent);
            
            if (isIOS && isSafari) {
                // Check for iOS 16 specifically
                const match = userAgent.match(/OS (\d+)_/);
                if (match && parseInt(match[1]) === 16) {
                    return true;
                }
            }
            return false;
        }

        // Show notice for iOS 16
        if (isIOS16()) {
            document.getElementById('ios16-notice').style.display = 'block';
            document.body.style.paddingTop = '200px';
            
            // Hide the main content
            const mainContent = document.querySelector('[data-testid="stAppViewContainer"]');
            if (mainContent) {
                mainContent.style.display = 'none';
            }
        }

        // Also show notice if there's a regex error (fallback)
        window.addEventListener('error', function(e) {
            if (e.message && e.message.includes('Invalid regular expression')) {
                document.getElementById('ios16-notice').style.display = 'block';
                document.body.style.paddingTop = '200px';
                
                // Hide the main content
                const mainContent = document.querySelector('[data-testid="stAppViewContainer"]');
                if (mainContent) {
                    mainContent.style.display = 'none';
                }
            }
        });
        </script>
        """
        st.components.v1.html(ios16_notice, height=0)
        
        # Stop execution
        st.stop()

def get_user_email():
    """Get the current user's email if authorized"""
    if check_beta_access():
        return st.session_state.user_email
    return None

def logout():
    """Log out the current user"""
    # Clear session state
    if "user_email" in st.session_state:
        del st.session_state.user_email
    if "remember_me" in st.session_state:
        del st.session_state.remember_me
    
    # Clear saved session file
    try:
        if os.path.exists("data/user_session.json"):
            os.remove("data/user_session.json")
    except Exception:
        pass  # Silently fail if we can't remove the file
    
    st.rerun() 