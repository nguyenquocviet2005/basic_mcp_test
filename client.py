from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
import os
import json
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
server_params = StdioServerParameters(
    command = 'mcp',
    args = ['run', 'server.py'],
    env = None
)

def convert_to_llm_tool(tool):
    tool_schema = {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": {
                "type": "object",
                "properties": tool.inputSchema["properties"],
                # "required": list(tool.inputSchema["properties"].keys())  # Make all properties required
            }
        }
    }
    return tool_schema

def call_llm(prompt, functions):
    client = OpenAI(api_key = os.environ["OPENAI_API_KEY"])
    print("CALLING LLM")
    response = client.chat.completions.create(
        model = 'gpt-4.1-nano',  # Fixed model name
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        tools = functions,
        temperature = 1.0,
        max_tokens = 1000,
        top_p = 1.0
    )
    print(f'RESPONSE: {response}')
    response_message = response.choices[0].message
    functions_to_call = []
    if response_message.tool_calls:
        for tool_call in response_message.tool_calls:
            print("TOOL:", tool_call)
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            functions_to_call.append({"name": name, "args": args})  # Fixed variable name

    return functions_to_call


async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("LIST TOOLS")
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f'Tool: {tool.name}')

            print("LIST RESOURCES")
            resources = await session.list_resources()
            for resource in resources:
                print(f'Resource: {resource}')

            # print("READING RESOURCE")
            # content, mime_type = await session.read_resource("greeting://hello")
            # print(f"Resource content: {content}")
            # print(f"MIME type: {mime_type}")
            
            # # Extract the actual text content from the resource
            # # Based on the output, content is ('meta', None) and mime_type is ('contents', [...])
            # if isinstance(mime_type, tuple) and len(mime_type) > 1:
            #     actual_contents = mime_type[1]  # Get the contents list
            #     if actual_contents:
            #         for item in actual_contents:
            #             print(item)
            #             if hasattr(item, 'text'):
            #                 print(f"Resource text: {item.text}")
            #             if hasattr(item, 'mimeType'):
            #                 print(f"Resource MIME type: {item.mimeType}")

            # print("CALL TOOL")
            # result = await session.call_tool('add', arguments = {'a': 1, 'b': 7})
            # print(f"Tool result: {result.content}")
            
            # # Extract the actual text content from the tool result
            # if result.content:
            #     for item in result.content:
            #         if hasattr(item, 'text'):
            #             print(f"Tool result value: {item.text}")
            functions = []
            for tool in tools.tools:
                print("Tool: ", tool.name)
                print("Tool", tool.inputSchema["properties"])
                functions.append(convert_to_llm_tool(tool))

            prompt = "Subtract 2 from 20"
            functions_to_call = call_llm(prompt, functions)
            
            for f in functions_to_call:
                result = await session.call_tool(f["name"], arguments = f["args"])
                print(f"Tool '{f['name']}' called with args {f['args']}")
                print("Tool result:", end=" ")
                if result.content:
                    for item in result.content:
                        if hasattr(item, 'text'):
                            print(item.text)
                        else:
                            print(item)
                else:
                    print("No content returned")


if __name__ == "__main__":
    asyncio.run(run())