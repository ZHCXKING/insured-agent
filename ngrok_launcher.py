# %%
import os
import logging
import ngrok
import signal
import threading
from dotenv import load_dotenv
# %%
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Ngrok")
# %%
def start_ngrok():
    port = int(os.getenv("PORT"))
    token = os.getenv("NGROK_AUTHTOKEN")
    try:
        listener = ngrok.forward(port, authtoken=token)
        print(f"本地目标: http://localhost:{port}")
        print(f"公网地址: {listener.url()}")
        stop_event = threading.Event()
        def exit_handler(sig, frame):
            logger.info("正在关闭 ngrok...")
            stop_event.set()
        signal.signal(signal.SIGINT, exit_handler)
        signal.signal(signal.SIGTERM, exit_handler)
        stop_event.wait()
    except Exception as e:
        logger.error(f"ngrok 运行出错: {e}")
    finally:
        ngrok.disconnect()
        logger.info("ngrok 已断开连接")
if __name__ == "__main__":
    start_ngrok()