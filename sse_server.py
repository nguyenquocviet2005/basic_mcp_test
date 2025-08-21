from starlette.applications import Starlette
from starlette.routing import Mount
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My App")
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers"""
    return a + b

@mcp.resource("greeting://{name}")
def get_greeting(name):
    return f"Hello, {name}"



app = Starlette(
    routes = [
        Mount('/', app=mcp.sse_app()),
    ]
)



if __name__ == "__main__":
    import uvicorn
    # Use import string and enable reload so changes are picked up automatically
    uvicorn.run("sse_server:app", host="127.0.0.1", port=8000, reload=True)