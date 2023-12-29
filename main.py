import os
from openai import OpenAI
import json
import audio_generator

function_schema = {
    "name": "formatAsJson",
    "parameters": {
        "type": "object",
        "properties": {
            "prompts": {
                "type": "array",
                "items": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            }
        },
        "required": ["prompts"]
    }
}

client = OpenAI(
    # This is the default and can be omitted
    api_key="",
)

file = open("QA.txt")
qua = file.read()

messages=[
        {"role": "system",
         "content": "Your are an intelligent system that extracts prompts from a questionnaire to be used with a generative ai model. Your primary role is to analyze and interpret the responses to this questionnaire, which is focused on eliciting detailed descriptions of personal memories that users wish to re-experience through audio. From the user's descriptions, you will identify and extract four key sound events that are pivotal to each memory. For each identified sound event, you are tasked with generating 10 distinct but closely related prompts. These prompts will be used by a generative AI model to create audio files that encapsulate the essence of the sound events. The challenge lies in ensuring that each set of prompts remains true to the core idea of its corresponding sound event, while introducing subtle variations to offer a range of auditory experiences. This process aims to recreate a multi-faceted and immersive auditory representation of the user's cherished memories."},
        {"role": "user", "content": "Please extract 4 key sound events from the following Q&A and generate 10 prompts for each sound event. The Q&A is focused on eliciting detailed descriptions of personal memories that users wish to re-experience through audio. The prompts will be used by a generative AI model to create audio files that encapsulate the essence of the sound events. Please ensure that each set of prompts remains true to the core idea of its corresponding sound event, while introducing subtle variations to offer a range of auditory experiences. Do not use verbs like create, generate, synthesize ... but rather just describe the audio and the scene. \n Q&A: \n" + qua},
    ]

def main():
    completion = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        functions=[function_schema],
        function_call={"name": "formatAsJson"}
    )

    # Retrieve the function call from the response
    function_call = completion.choices[0].message.function_call

    # Parse the arguments as JSON
    json_output = json.loads(function_call.arguments)

    # convert the prompts to a list of lists
    python_list = json_output.get("prompts", [])

    print("starting generation process")
    audio_gen = audio_generator.AudioGenerator()
    audio_gen.start_generation_process(python_list)

if __name__ == "__main__":
    main()


