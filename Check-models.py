from dotenv import load_dotenv
import os
from groq import Groq

#Load environment variables
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

#Fetch the list of models
#The models.list() call returns a SyncCursorPage object
models = client.models.list()

print("Models available for your key:")
#Access the 'data' attribute to iterate through the model objects for model in models.data:
  print(f" - {model.id}")
