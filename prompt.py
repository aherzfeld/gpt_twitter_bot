

system_directive = """
    Act as a social media manager and twitter expert.

    You will receive the text from an article and you will return a tweet to 
    introduce and promote the article on twitter. The tone should be friendly, 
    but professional. The tweet should be no longer than 180 characters.
"""

def generate_prompt(system_directive, text):
    messages = [
        {'role': 'system', 'content': system_directive},
        {'role': 'user', 'content': f"Create a tweet for this article: {text}"}
    ]
    return messages
