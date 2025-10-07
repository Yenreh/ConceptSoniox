import os
import http.client
import json
import base64
from dotenv import load_dotenv

load_dotenv()

def transcribe_local_audio(file_path):
    url = "api.deepgram.com"
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        raise ValueError("DEEPGRAM_API_KEY not set in .env")
    with open(file_path, "rb") as audio_file:
        audio_data = audio_file.read()
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "audio/*"
    }
    conn = http.client.HTTPSConnection(url)
    conn.request("POST", "/v1/listen", audio_data, headers)
    response = conn.getresponse()
    response_data = response.read()
    conn.close()
    return json.loads(response_data)

def transcribe_remote_audio(audio_url):
    url = "api.deepgram.com"
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        raise ValueError("DEEPGRAM_API_KEY not set in .env")
    payload = json.dumps({"url": audio_url})
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json"
    }
    conn = http.client.HTTPSConnection(url)
    conn.request("POST", "/v1/listen", payload, headers)
    response = conn.getresponse()
    response_data = response.read()
    conn.close()
    return json.loads(response_data)

def text_to_speech(text, model, output_file_path, encoding, sample_rate, mip_opt_out):
    url = "api.deepgram.com"
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        raise ValueError("DEEPGRAM_API_KEY not set in .env")
    request_body = json.dumps({"text": text})
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json"
    }
    query = f"/v1/speak?model={model}&encoding={encoding}&sample_rate={sample_rate}"
    if mip_opt_out == "true":
        query += "&mip_opt_out=true"
    conn = http.client.HTTPSConnection(url)
    conn.request("POST", query, request_body, headers)
    response = conn.getresponse()
    with open(output_file_path, "wb") as output_file:
        output_file.write(response.read())
    conn.close()
    return output_file_path
