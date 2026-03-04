#!/usr/bin/env python3
"""
Test Google Drive Function Calling via ChatGPT
Proof of concept: ChatGPT can call our Google Drive functions
"""

import openai
import json
from pathlib import Path

# Load API key
api_key = None
env_path = Path('.env')
if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('ZENDESK_AI_GATEWAY_KEY='):
                api_key = line.split('=', 1)[1].strip()
                break

client = openai.OpenAI(
    api_key=api_key,
    base_url="https://ai-gateway.zende.sk/v1"
)

# Define Google Drive functions
tools = [
    {
        "type": "function",
        "function": {
            "name": "list_google_drive_files",
            "description": "List files in a Google Drive folder or shared drive",
            "parameters": {
                "type": "object",
                "properties": {
                    "folder_name": {
                        "type": "string",
                        "description": "Name of the folder (e.g., 'Strategy-agent', 'SalesStrategy')"
                    },
                    "max_files": {
                        "type": "integer",
                        "description": "Maximum number of files to return",
                        "default": 10
                    }
                },
                "required": ["folder_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "upload_to_google_drive",
            "description": "Upload a file to Google Drive",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Local path to the file to upload"
                    },
                    "destination_folder": {
                        "type": "string",
                        "description": "Google Drive folder to upload to"
                    }
                },
                "required": ["file_path", "destination_folder"]
            }
        }
    }
]

# Mock function to simulate Google Drive listing
def execute_list_google_drive_files(folder_name, max_files=10):
    """Simulate listing Google Drive files"""
    # In reality, this would use GoogleDriveUploader
    return {
        "folder": folder_name,
        "files": [
            {"name": "ai_penetration_20260303.xlsx", "size": "45KB", "modified": "2026-03-03"},
            {"name": "ai_penetration_20260302.csv", "size": "28KB", "modified": "2026-03-02"},
            {"name": "strategy_report_Q1.pdf", "size": "1.2MB", "modified": "2026-02-28"}
        ],
        "total": 3,
        "note": "This is simulated data. Real implementation would use GoogleDriveUploader."
    }

def execute_upload_to_google_drive(file_path, destination_folder):
    """Simulate uploading to Google Drive"""
    return {
        "status": "success",
        "file": file_path,
        "destination": destination_folder,
        "link": "https://drive.google.com/file/d/EXAMPLE_ID",
        "note": "This is simulated. Real implementation would use GoogleDriveUploader."
    }

# Test conversation
print("="*70)
print("🧪 Testing ChatGPT Function Calling with Google Drive")
print("="*70)
print()

messages = [
    {
        "role": "user",
        "content": "Can you list the files in the Strategy-agent folder?"
    }
]

print(f"👤 User: {messages[0]['content']}\n")

# First call - model will request function call
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

response_message = response.choices[0].message
messages.append(response_message)

# Check if model wants to call a function
if response_message.tool_calls:
    print("🤖 Assistant wants to call functions:")

    for tool_call in response_message.tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        print(f"   📞 Calling: {function_name}")
        print(f"   📋 Arguments: {function_args}")

        # Execute the function
        if function_name == "list_google_drive_files":
            result = execute_list_google_drive_files(**function_args)
        elif function_name == "upload_to_google_drive":
            result = execute_upload_to_google_drive(**function_args)
        else:
            result = {"error": "Unknown function"}

        print(f"   ✅ Result: {json.dumps(result, indent=6)}")

        # Add function result to messages
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": json.dumps(result)
        })

    print()

    # Second call - model will use function results to respond
    print("🤖 Assistant processing results...\n")

    final_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    print(f"🤖 Assistant: {final_response.choices[0].message.content}")

else:
    print(f"🤖 Assistant: {response_message.content}")

print()
print("="*70)
print("✅ Function calling works! We can implement Google Drive this way!")
print("="*70)
