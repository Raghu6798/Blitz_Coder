import os 
from dotenv import load_dotenv
import requests

from tenacity import retry,stop_after_attempt,wait_fixed,retry_if_exception_type

load_dotenv()

from langfuse.langchain import CallbackHandler
from langfuse import Langfuse



@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    retry=retry_if_exception_type((requests.exceptions.RequestException,)),
    reraise=True,
)
def init_langfuse():
    return Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host="https://us.cloud.langfuse.com",
    )

print(init_langfuse())