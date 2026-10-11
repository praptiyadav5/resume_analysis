import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv(Path(__file__).with_name(".ENV"))

client = genai.Client(api_key=os.environ["GENAIKEY"])

for m in client.models.list():
    print(m.name)