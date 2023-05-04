import requests
from dotenv import dotenv_values
import os
import openai
import json
from typing import Optional
import argparse

def generate_quote(prompt: str):
    # Get an interesting quote from chatgpt
    completion = openai.Completion.create(
        model="text-davinci-003", 
        max_tokens=500,
        temperature=0.7,
        presence_penalty=0.6,
        prompt=prompt)
    inspirational_quote = completion.choices[0].text
    return inspirational_quote

def clean_text(text: str):
    return text.strip().lstrip("\"").rstrip("\"")

def post_to_linkedin(post_text: str, user_id: str, bearer_token: str, img: Optional[str] = None):
        
    # Post the quote to LinkedIn
    linked_headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
        "x-li-format": "json"
    }
    data = json.dumps({
        "author": f"urn:li:person:{user_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": post_text
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    })

    res = requests.request(
        "POST",
        "https://api.linkedin.com/v2/ugcPosts",
        headers=linked_headers,
        data=data
    )

    print(res)  

def main(send_to_linkedin: bool, user_id: Optional[str] = None, bearer_token: Optional[str] = None):

    inspirational_quote = clean_text(generate_quote())
    print(inspirational_quote)

    if (send_to_linkedin and user_id and bearer_token):
        post_to_linkedin(inspirational_quote, user_id=user_id, bearer_token=bearer_token)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                    prog='Cat Pirate Quotes',
                    description='Uses chatGPT to generate text and post it somewhere',
                    epilog='Use with caution - who knows what chatGPT will say!')

    parser.add_argument('-l', '--post', action='store_true')
    parser.add_argument('-p', '--prompt', default="Write a 125 word inspirational quote for linkedIn for an audience of people struggling to find a job that is sure to get a big response")
    args = parser.parse_args();

    config = dotenv_values(".env") # take environment variables from .env.
    if os.path.exists(".env.development"):
        config = dotenv_values(".env.development")

    linkedin_user_id = config["LINKEDIN_USER_ID"]
    linkedin_bearer_token = config["LINKEDIN_APIKEY"]
    openAiApiKey = config["OPENAI_API_KEY"]
    openai.api_key = openAiApiKey
    
    main(args.post, linkedin_user_id, linkedin_bearer_token)