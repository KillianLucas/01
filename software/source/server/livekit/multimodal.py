from __future__ import annotations
import sys
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import openai
from dotenv import load_dotenv
import os
import time
from typing import Annotated
from livekit.agents import llm

# Set the environment variable
os.environ['INTERPRETER_TERMINAL_INPUT_PATIENCE'] = '200000'

instructions = """
You are Open Interpreter, a world-class programmer that can complete any goal by executing code.
For advanced requests, start by writing a plan.
When you execute code, it will be executed **on the user's machine** in a stateful Jupyter notebook. The user has given you **full permission** to execute any code necessary to complete the task. Execute the code. You CAN run code on the users machine, using the tool you have access to.
You can access the internet. Run **any code** to achieve the goal, and if at first you don't succeed, try again and again.
You can install new packages.
If you modify or create a file, YOU MUST THEN OPEN IT to display it to the user.
Be concise. Do NOT send the user a markdown version of your code — just execute the code instantly. Execute the code!

You are capable of **any** task.

You MUST remember to pass into the execute_code function a correct JSON input like {"code": "print('hello world')"} and NOT a raw string or something else.
"""

load_dotenv()

async def entrypoint(ctx: JobContext):
    
    from interpreter import interpreter

    def execute_code(code):
        print("--- code ---")
        print(code)
        print("---")
        #time.sleep(2)
        # Check if the code contains any file deletion commands
        if any(keyword in code.lower() for keyword in ['os.remove', 'os.unlink', 'shutil.rmtree', 'delete file', 'rm -']):
            print("Warning: File deletion commands detected. Execution aborted for safety.")
            return "Execution aborted: File deletion commands are not allowed."
        print("--- output ---")
        output = ""
        for chunk in interpreter.computer.run("python", code):
            if "content" in chunk and type(chunk["content"]) == str:
                output += "\n" + chunk["content"]
                print(chunk["content"])
        print("---")

        output = output.strip()
        
        if output == "":
            output = "No output was produced by running this code."
        return output


    # first define a class that inherits from llm.FunctionContext
    class AssistantFnc(llm.FunctionContext):
        # the llm.ai_callable decorator marks this function as a tool available to the LLM
        # by default, it'll use the docstring as the function's description
        @llm.ai_callable()
        async def execute(
            self,
            # by using the Annotated type, arg description and type are available to the LLM
            code: Annotated[
                str, llm.TypeInfo(description="The Python code to execute")
            ],
        ):
            """Executes Python and returns the output"""
            return execute_code(code)

    fnc_ctx = AssistantFnc()

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    participant = await ctx.wait_for_participant()

    openai_api_key = os.getenv("OPENAI_API_KEY")
    model = openai.realtime.RealtimeModel(
        instructions=instructions,
        voice="shimmer",
        temperature=0.6,
        modalities=["audio", "text"],
        api_key=openai_api_key,
        base_url="wss://api.openai.com/v1",
    )
    model._fnc_ctx = fnc_ctx
    assistant = MultimodalAgent(model=model, fnc_ctx=fnc_ctx)

    assistant.start(ctx.room)

    # Create a session with the function context
    session = model.session(
        chat_ctx=llm.ChatContext(),
        fnc_ctx=fnc_ctx,
    )

    # Send a message to the client to switch to multimodal mode
    await ctx.room.local_participant.publish_data(payload="{MULTIMODAL_MODE}", topic="agent_mode")

    # Initial message to start the interaction
    session.conversation.item.create(
      llm.ChatMessage(
        role="user",
        content="Hello!",
      )
    )
    session.response.create()

def main(livekit_url):
    # Workers have to be run as CLIs right now.
    # So we need to simulate running "[this file] dev"

    # Modify sys.argv to set the path to this file as the first argument
    # and 'dev' as the second argument
    sys.argv = [str(__file__), 'dev']

    # Initialize the worker with the entrypoint
    cli.run_app(
        WorkerOptions(entrypoint_fnc=entrypoint, api_key="devkey", api_secret="secret", ws_url=livekit_url, port=8082)
    )