from langchain.utilities import GoogleSerperAPIWrapper, WikipediaAPIWrapper
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.callbacks import get_openai_callback
import argparse
import requests
from bs4 import BeautifulSoup
import re

def get_text_from_url(url: str) -> str:
    try:
        if url.startswith("'") and url.endswith("'"):
            url = url[1:-1]
        # Fetch the web content
        response = requests.get(url)
        response.raise_for_status()
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract the text and remove HTML tags
        text = soup.get_text()
        # Remove extra lines, empty lines, and unnecessary whitespace
        cleaned_text = re.sub(r'\n+', '\n', text)  # Remove extra lines
        cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text)  # Remove empty lines
        cleaned_text = cleaned_text.strip()  # Remove leading/trailing whitespace

        return cleaned_text

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return


parser = argparse.ArgumentParser(description="A scrpit to run the langchain with google search")
params = (
    ("--serper_api_key", "-s","Serper API key"),
    ("--openai_api_key", "-o","OpenAI API key"),
    ("--prompt", "-p",   "Prompt to run the langchain with google search agent"),
)

for full_param, abbr_param, _help in params:
    parser.add_argument(full_param, abbr_param, help= _help)

parser.add_argument("--google_location", "-gl", help="Google location", default="TW")


args = parser.parse_args()


token_lookup = {
    "gpt-3.5-turbo": 4097,
    "gpt-4": 8192,
    "gpt-3.5-turbo-16k": 16385,
    "gpt-4-32k": 32768,
}


all_models = ["gpt-3.5-turbo", "gpt-4", "gpt-3.5-turbo-16k", "gpt-4-32k"]

prompt = f'''
Please answer the question: 
{args.prompt}
Please follow the following guidelines:
    - If searched content is too lengthy (greater than 10000 words), you should immediately stop due to token limit you have.
    - Try your best to summarize your observation (not with a tool but with your reasoning ability) under 200 words due to token limit you have.

'''

with get_openai_callback() as cb:
    llm = ChatOpenAI(temperature=0, openai_api_key= args.openai_api_key,
                    model_name="gpt-3.5-turbo-16k")
    search = GoogleSerperAPIWrapper(serper_api_key=args.serper_api_key, gl= args.google_location)
    wiki_search = WikipediaAPIWrapper()
    tools = [
        Tool(
            name="Google Search",
            func=search.run,
            description="Useful for when you need to ask with google search, use this with a keyword or a question",
        ),
        Tool(
            name="Reqeust Page",
            func=get_text_from_url,
            description="Useful for when you need to get the content of a web page url, make sure your url is a valid Pyhton string having a valid connection adapter",
        ),
        Tool(
            name="Wikipedia Search",
            func=wiki_search.run,
            description="Useful for when you need to look up a topic, country or person on wikipedia, don't abuse this tool, only use it when you need to",
        )
    ]

    self_ask_with_search = initialize_agent(
        tools, llm, 
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
        verbose= True, 
        return_intermediate_steps=True, 
        max_iteration= 5,
        early_stopping_method='generate',
        handle_parsing_errors=True,
    )
    result = self_ask_with_search({"input":prompt})
    print(cb)
