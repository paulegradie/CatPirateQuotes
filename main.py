import requests
from dotenv import dotenv_values
import os
import openai
import json

config = dotenv_values(".env") # take environment variables from .env.
if os.path.exists(".env.development"):
    config = dotenv_values(".env.development")

openAiApiKey = config["OPENAI_API_KEY"]
linkedInAuthKey = config["LINKEDIN_APIKEY"]
linkedin_user_id = config["LINKEDIN_USER_ID"]
openai.api_key = openAiApiKey

# Get an interesting quote from chatgpt
completion = openai.Completion.create(
    model="text-davinci-003", 
    max_tokens=500,
    temperature=0.7,
    presence_penalty=0.6,
    prompt="Write a 125 word inspirational quote for linkedIn for an audience of people struggling to find a job that is sure to get a big response")
inspirational_quote = completion.choices[0].text

clean_inspirational_quote = inspirational_quote.strip().lstrip("\"").rstrip("\""))
print(clean_inspirational_quote)

# Post the quote to LinkedIn
linked_headers = {
    "Authorization": f"Bearer {linkedInAuthKey}",
    "Content-Type": "application/json",
    "x-li-format": "json"
}
data = json.dumps({
    "author": f"urn:li:person:{linkedin_user_id}",
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {
                "text": clean_inspirational_quote
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