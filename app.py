import openai
from dotenv import dotenv_values
import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import tiktoken

from utilities.helpers import num_tokens_from_messages

config = dotenv_values('.env')
openai.api_key = config['OPENAI_API_KEY']

model = 'gpt-3.5-turbo' # make this a dynamic user choice

st.title('Sojourn Twitter Bot')
article_url = st.text_input("Enter the post's URL")

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


# https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb

def num_tokens_from_messages(messages, model):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        return num_tokens_from_messages(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


text = extract_article_text(
    request_article(article_url),
    check_url(article_url)
)


# use tiktoken to calculate the number of tokens in list of messages