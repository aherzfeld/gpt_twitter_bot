import openai
from dotenv import dotenv_values
import streamlit as st
import requests
from bs4 import BeautifulSoup


config = dotenv_values('.env')
openai.api_key = config['OPENAI_API_KEY']

st.title('Sojourn Twitter Bot')
post_url = st.text_input("Enter the post's URL")

def request_post(post_url):
    try:
        r = requests.get(post_url)
        r.raise_for_status()  # This will raise an HTTPError for bad responses (4XX and 5XX)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")
    else:
        print(f"Request for {post_url} was successful")
        return r

r = request_post(post_url)

soup = BeautifulSoup(r.text, 'html.parser')

# I'm at the point of deciding how to differentiate between sojourn & substack

# content = soup.get_text()
# print(len(content))
post_content = soup.find('div', class_='body markup')
if post_content:
    text_content = post_content.get_text()
    print(len(text_content))
else:
    print("Article content not found")  

