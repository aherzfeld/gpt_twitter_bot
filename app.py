import openai
from dotenv import dotenv_values
import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import tiktoken

from helpers import num_tokens_from_messages
from prompt import system_directive, generate_prompt


def request_article(article_url):
    try:
        r = requests.get(article_url)
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
        print(f"Request for {article_url} was successful")
        return r


def check_url(url):
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname

    if 'sojourn' in hostname:
        return 'sojourn'
    elif 'substack' in hostname:
        return 'substack'
    else:
        return hostname
    
def extract_article_text(
        response,
        hostname,
):
    soup = BeautifulSoup(response.text, 'html.parser')

    if hostname == 'sojourn':
        # parse sojourn style
        article_content = soup.find('div', class_='blog-item-content-wrapper')
        text = article_content.get_text()
        print(f'Sojourn article extracted. Length: {len(text)}')
        return text
    elif hostname == 'substack':
        article_content = soup.find('div', class_='body markup')
        text = article_content.get_text()
        print(f'Substack article extracted. Length: {len(text)}')
        return text
    else: # come up with a way to extract cleaner text from general sites
        text = soup.get_text()
        print(f'Article extracted. Length: {len(text)}')
        return text


def create_tweet(messages, model):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
    )
    messages.append(response['choices'][0]['message'])
    return response['choices'][0]['message']['content']


# run application below

config = dotenv_values('.env')
openai.api_key = config['OPENAI_API_KEY']

model = 'gpt-3.5-turbo' # make this a dynamic user choice

st.title('Sojourn Twitter Bot')
article_url = st.text_input("Enter the post's URL")

if article_url:
    text = extract_article_text(
        request_article(article_url),
        check_url(article_url)
    )

    messages = generate_prompt(
        system_directive, 
        text
    )

    num_tokens = num_tokens_from_messages(messages, model)
    print(f'The messages total {num_tokens} tokens.')

    st.write(create_tweet(messages, model))

    # create buttons for accept and retry
    try_again = st.button(label='Try Again')


