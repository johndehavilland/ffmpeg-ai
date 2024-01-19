import os
from openai import AzureOpenAI
import json
import requests

from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_KEY"),  
  api_version="2023-12-01-preview"
)


# Example function hard coded to return the same weather
# In production, this could be your backend API or an external API
def run_ffmpeg(command):
    print("tool called with command: ", command)
    """Run FFMPEG Command"""
    # Define the API endpoint
    api_url = "http://localhost:5000/ffmpeg"

    # Define the FFmpeg command
    #ffmpeg_command = "ffmpeg -i input_video.mp4 -vf \"select='not(mod(t,10))',setpts=N/FRAME_RATE/TB\" -vsync vfr output_frames_%04d.png"
    ffmpeg_command = command
    # Create a JSON payload
    payload = {'command': ffmpeg_command}

    # Make a POST request to the API
    response = requests.post(api_url, json=payload)

    # Print the response
    print(response.json())

def run_conversation():
    # Step 1: send the conversation and available functions to the model
    # messages = [{"role": "user", "content": "Extract frames every 1 seconds from a video called input.mp4"}]
    # messages = [{"role": "user", "content": "Create a 2x slower video from input.mp4 and store it in /mnt/data"}]
    messages = [{"role": "user", "content": "Extract audio from input.mp4 and store it in /mnt/data"}]


    tools = [
        {
            "type": "function",
            "function": {
                "name": "run_ffmpeg",
                "description": "run ffmpeg commands",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command    ": {
                            "type": "string",
                            "description": "The specific ffmpeg command to run",
                        }
                    },
                    "required": ["command"],
                },
            },
        }
    ]
    response = client.chat.completions.create(
        model="gpt35-turbo-latest",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message
    print(response_message)
    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "run_ffmpeg": run_ffmpeg,
        }  # only one function in this example, but you can have multiple
        messages.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                command=function_args.get("command")
            )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        second_response = client.chat.completions.create(
            model="gpt35-turbo-latest",
            messages=messages,
        )  # get a new response from the model where it can see the function response
        return second_response
print(run_conversation())