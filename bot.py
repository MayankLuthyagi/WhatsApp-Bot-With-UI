import streamlit as st
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Access user data directory and profile from secrets.toml
user_data_dir = st.secrets["whatsapp"]["user_data_dir"]
profile_directory = st.secrets["whatsapp"]["profile_directory"]
url = st.secrets["whatsapp"]["url"]

# Streamlit Input
group_name = st.text_input("Enter the WhatsApp Group Name:")
message = st.text_area("Enter your message:")
send_button = st.button("Send Message")

# Initialize the driver only once
if 'driver' not in st.session_state:
    st.session_state.driver = None

def initialize_driver():
    """Initialize and return the WebDriver with the user data directory."""
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")
    # Set user data directory and profile
    options.add_argument(f"user-data-dir={user_data_dir}")  # Path to your Chrome user data
    options.add_argument(f"profile-directory={profile_directory}")  # Path to your specific profile

    # Automatically download and use the correct chromedriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def send_message(driver, group_name, message):
    """Send the message to the specified WhatsApp group."""
    try:
        driver.get(url)

        # Wait for the WhatsApp Web to load
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[@id='pane-side']")))

        # Locate the group by title
        group = None
        try:
            group = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, f"//span[@title='{group_name}']"))
            )
            group.click()
        except Exception as e:
            st.error(f"Group with name '{group_name}' not found. Make sure it's visible in WhatsApp Web.")
            return

        # Find the message box and send the message
        text_box = driver.find_element(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div/div[1]/p')

        # Type and send the message
        for line in message.split('\n'):
            text_box.send_keys(line)  # Type the line
            text_box.send_keys(Keys.SHIFT, Keys.ENTER)  # Line break
            time.sleep(0.5)  # Adjust the delay if needed
        text_box.send_keys(Keys.ENTER)  # Send the message
        time.sleep(2)
        st.success("Message sent successfully!")
        driver.quit()
    except Exception as e:
        st.error(f"Error sending message: {e}")

# Trigger the send action when button is clicked
if send_button:
    if group_name and message:
        # Initialize the driver once and store it in session state
        if st.session_state.driver is None:
            st.session_state.driver = initialize_driver()

        send_message(st.session_state.driver, group_name, message)

    else:
        st.warning("Please enter both group name and message.")
