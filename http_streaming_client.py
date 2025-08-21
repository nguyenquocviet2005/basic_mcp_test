from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
import mcp.types as types
import logging
import requests
from mcp.shared.session import RequestResponder
import asyncio

logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt = '%Y-%m-%d %H:%M:%S' 
)
logger = logging.getLogger('mcp_client')

class LoggingCollector:
    def __init__(self):
        self.log_messages: list[types.LoggingMessageNotificationParams] = []

    async def __call__(self, params: types.LoggingMessageNotificationParams) -> None:
        self.log_messages.append(params)
        # logger.info("MCP Log: %s - %s", params.level, params.data)

logging_collector = LoggingCollector()
port = 8000

def stream_progress(message='hello', url='http://localhost:8000/stream'):
    params = {"message": message}
    logger.info("Connecting to %s with message: %s", url, message)

    try:
        with requests.get(url, params=params, stream=True, timeout=10) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode().strip()
                    print(decoded_line)
                    logger.debug("Stream content: %s", decoded_line)
            
            logger.info("--Stream Ended--")

    except requests.RequestException as e:
        logger.error("Error during streaming: %s", e)

async def message_handler(
    message: RequestResponder[types.ServerRequest, types.ClientResult]
    | types.ServerNotification
    | Exception,
) -> None:
    # logger.info(f'Received message: {message}')
    if isinstance(message, Exception):
        logger.error("Exception received")
        raise message
    
    elif isinstance(message, RequestResponder):
        logger.info(f'Request Responder: {message}')

    elif isinstance(message, types.ServerNotification):
        logger.info(f'Notification: {message}')
    
    else:
        logger.info(f'System Message: {message}')

async def main():
    async with streamablehttp_client(f'http://localhost:{port}/mcp') as (
        read_stream,
        write_stream,
        get_session_id,
    ):
        async with ClientSession(
            read_stream,
            write_stream,
            logging_callback=logging_collector,
            message_handler=message_handler
        ) as session:
            # id_before = get_session_id()
            # logger.info(f'Session ID before init: {id_before}')
            # await session.initialize()
            # id_after = get_session_id()
            # logger.info(f'Session ID after init: {id_after}')
            # logger.info("Session initialized, ready to call tools.")
            # tool_result = await session.call_tool('process_files', {"message": "Hello from client"})
            # logger.info(f"Tool result: {tool_result}")
            # if logging_collector.log_messages:
            #     logger.info("Collected log messages:")
            #     for log in logging_collector.log_messages:
            #         logger.info(f"Log: {log}")
            await session.initialize()
            tool_result = await session.call_tool('integer_calculation', arguments = {'a': 4, 'b': 5})
            logger.info(f'Tool result: {tool_result}')

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'mcp':
        logger.info("Running MCP client ...")
        asyncio.run(main())
    else:
        logger.info("Running classic HTTP streaming client")
        stream_progress(message="goodbye")






