import re
import json
import os
import requests
import logging

logger = logging.getLogger(__name__)

def get_iam_token(api_key: str) -> str:
    """Get IAM token for IBM Watson API"""
    token_response = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        data={
            "apikey": api_key,
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return token_response.json()["access_token"]

def call_llm(prompt: str, images: list | None = None, max_tokens: int = 4096) -> str:
    """
    Call IBM Watson AI API.
    Note: Images are not currently supported and will be ignored if provided.
    """
    api_key = os.environ["WATSON_API_KEY"]
    deployment_url = os.environ["WATSON_DEPLOYMENT_URL"]
    
    # Get access token
    access_token = get_iam_token(api_key)
    
    # Prepare the request - Watson only accepts 'messages' and optionally 'context', 'tools', etc.
    # max_tokens is not supported in Watson's text chat endpoint
    response = requests.post(
        deployment_url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        json={
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    )
    
    # Check if request was successful
    if response.status_code != 200:
        error_msg = f"Watson API error: {response.status_code} - {response.text}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    data = response.json()
    logger.debug(f"Watson API response: {json.dumps(data, indent=2)}")
    
    # Handle different possible response formats
    # Try the standard OpenAI-compatible format first
    if "choices" in data:
        content = data["choices"][0]["message"]["content"]
    # Try Watson's native format
    elif "results" in data:
        content = data["results"][0]["generated_text"]
    # Try direct content field
    elif "generated_text" in data:
        content = data["generated_text"]
    # Try another possible format
    elif "content" in data:
        content = data["content"]
    else:
        # If none of the expected formats match, raise an error with the response
        error_msg = f"Unexpected Watson API response format: {json.dumps(data, indent=2)}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    return content

def parse_llm_json(response: str) -> dict:
    """Parse JSON from LLM response, handling markdown fences."""
    cleaned = response.strip()
    cleaned = re.sub(r'^```(?:json)?\n?', '', cleaned)
    cleaned = re.sub(r'\n?```$', '', cleaned)
    return json.loads(cleaned.strip())

# Made with Bob
