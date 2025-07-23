import logging
import json
import datetime
from openai import AzureOpenAI
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

app = func.FunctionApp()
@app.route(route='openai_function_app', auth_level=func.AuthLevel.ANONYMOUS)
def openai_function_app(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('TRAPPUS Function received a request.')

    try:
        MODEL_NAME = "gpt-4o"  # Adjust to your deployed model ID if different
        credential=DefaultAzureCredential()
        client=SecretClient(vault_url='https://trappus-key-vault.vault.azure.net/',credential=credential)
        api_key = client.get_secret('OPENAI-API-KEY').value
        api_endpoint = client.get_secret('OPENAI-ENDPOINT').value
        # AzureOpenAI.api_type = 'azure'
        api_version = '2024-11-20'  # Replace with your actual deployed version
        #get_json()
        user_input = req.get_json().get('prompt')
        if not user_input:
            return func.HttpResponse("Missing 'prompt' in request body.", status_code=400)

        logging.info(f"User prompt: {user_input}")

        # Call OpenAI
        azure_openai_client=AzureOpenAI(azure_endpoint=api_endpoint,api_key=api_key,api_version=api_version)    
        response = azure_openai_client.chat.completions.create(
            engine=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are TRAPPUS, an automation assistant for Azure and WordPress."},
                {"role": "user", "content": user_input}
            ],
            temperature=0.3,
            max_tokens=500
        )
        if response:
         answer = response.choices[0].message.content
         logging.info(f"TRAPPUS response: {answer}")

        return func.HttpResponse(json.dumps({"response":answer}), status_code=200)

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(f"Internal server error: {str(e)}", status_code=500)
    
