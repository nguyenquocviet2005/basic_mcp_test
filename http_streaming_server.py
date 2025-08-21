from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from mcp.server.fastmcp import FastMCP, Context
import asyncio
import uvicorn
import os
from mcp.types import (TextContent)

app = FastAPI()

# Define an MCP server instance for the optional streamable-http mode
mcp = FastMCP("Demo")

async def event_stream(message: str):
    for i in range(1,4):
        yield f"Processing file {i}/3...\n"
        await asyncio.sleep(1)
    yield f"Here's the file content: {message}\n"

@app.get("/stream")
async def stream(message: str = "hello"):
    return StreamingResponse(event_stream(message), media_type="text/plain")

@mcp.tool(description="A tool that simulates file processing and sends progress notifications")
async def process_files(message: str, ctx: Context) -> TextContent:
    files = [f'files_{i}.txt' for i in range(1,4)]
    for idx, file in enumerate(files, 1):
        await ctx.info(f"Processing file {idx}/{len(files)}...")
        await asyncio.sleep(1)
    await ctx.info("All files processed!")
    return TextContent(type="text", text=f"Processed files: {', '.join(files)} | Message: {message}")

@mcp.tool(description='A tool that perform mathematical calculation for two integers')
async def integer_calculation(a: int, b: int, ctx: Context) -> int | float:
    calculation = {}
    sum = a + b
    calculation['sum'] = sum
    await ctx.info(f"Sum of {a} and {b}: {sum}")
    await asyncio.sleep(1)

    difference = a - b
    calculation['difference'] = difference
    await ctx.info(f"Difference of {a} and {b}: {difference}")
    await asyncio.sleep(1)

    product = a * b
    calculation['product'] = product
    await ctx.info(f"Product of {a} and {b}: {product}")
    await asyncio.sleep(1)

    quotient = a / b
    calculation['quotient'] = quotient
    await ctx.info(f'Quotient of {a} and {b}: {quotient}')
    await asyncio.sleep(1)
    
    return calculation

if __name__ == "__main__":
    import sys
    if "mcp" in sys.argv:
        print("Starting MCP Server with streamable-http transport...")
        mcp.run(transport='streamable-http')
    else:
        print("Starting FastAPI server for classic HTTP streaming...")
        uvicorn.run("http_streaming_server:app", host="127.0.0.1", port=8000, reload=True)