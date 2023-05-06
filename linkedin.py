import requests
from dotenv import dotenv_values
import os
import openai
import json
from typing import Optional
import argparse


def generate_quote(prompt: str, model: str):
    completion = openai.Completion.create(
        model=model,
        max_tokens=500,
        temperature=0.7,
        presence_penalty=0.6,
        prompt=prompt)
    inspirational_quote = completion.choices[0].text
    return inspirational_quote


def clean_text(text: str):
    return text.strip().lstrip("\"").rstrip("\"")


def post_to_linkedin(post_text: str, user_id: str, bearer_token: str, img: Optional[str] = None):
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
        data=data)
    print(res)


def main(
        prompt: str,
        model: str,
        send_to_linkedin: bool,
        user_id: Optional[str] = None,
        bearer_token: Optional[str] = None):

    inspirational_quote = clean_text(generate_quote(prompt, model))
    print(inspirational_quote)

    if (send_to_linkedin and user_id and bearer_token):
        post_to_linkedin(inspirational_quote, user_id=user_id,
                         bearer_token=bearer_token)


if __name__ == "__main__":
    DEFAULT_PROMPT = "Write a 125 word inspirational quote for linkedIn for an audience of people struggling to find a job that is sure to get a big response"
    parser = argparse.ArgumentParser(
        prog='Cat Pirate Quotes - LinkedIn',
        description='Uses chatGPT to generate text and post it to LinkedIn',
        epilog='Use with caution - who knows what chatGPT will say!')
    parser.add_argument('-s', '--post', required=False, action='store_true')
    parser.add_argument('-m', '--model', required=False,
                        default="text-davinci-003")
    parser.add_argument('-p', '--prompt', default=DEFAULT_PROMPT)

    if os.path.exists(".env.development"):
        config = dotenv_values(".env.development")
        linkedin_user_id = config["LINKEDIN_ID"]
        linkedin_bearer_token = config["LINKEDIN_TOKEN"]
        openAiApiKey = config["OPENAI_APIKEY"]
        args = parser.parse_args()

    else:
        parser.add_argument('-u', '--linkedin-id', required=True)
        parser.add_argument('-l', '--linkedin-token', required=True)
        parser.add_argument('-o', '--openai-apikey', required=True)
        args = parser.parse_args()
        linkedin_user_id = args.linkedin_id
        linkedin_bearer_token = args.linkedin_token

    openai.api_key = openAiApiKey
    main(
        args.prompt,
        args.model,
        args.post,
        linkedin_user_id,
        linkedin_bearer_token)
