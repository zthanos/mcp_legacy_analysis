import os
from dotenv import load_dotenv
import logging

logging.basicConfig(
    filename="mcp_debug.log",
    filemode='a',
    encoding='utf-8',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

from legacy_analysis_server import mcp
if __name__ == "__main__":
    load_dotenv()
    logger = logging.getLogger("mcp_logger")
    # logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler("mcp_debug.log", mode='a', encoding='utf-8')
    # formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)    
    mcp.run()