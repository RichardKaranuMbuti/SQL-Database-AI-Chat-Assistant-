
from dotenv import load_dotenv
import os
load_dotenv()
from langchain_ibm import WatsonxLLM

credentials = {
    "url": "https://eu-de.ml.cloud.ibm.com",
    "apikey": os.getenv("apikey") ,  
    "project_id": os.getenv("project_id")
}

param = {
    "decoding_method": "greedy",
    "temperature": 0.6, 
    "min_new_tokens": 1000,
    "max_new_tokens": 2500,
    "stop_sequences":['\nObservation', '\n\n']
    }
models = {"ibm" : "ibm/granite-13b-chat-v2",
          "llama" : "meta-llama/llama-3-1-70b-instruct",
          }


watsonx_llm = WatsonxLLM(
    model_id =  "meta-llama/llama-3-1-70b-instruct",
    url = credentials.get("url"),
    apikey = credentials.get("apikey"),
    project_id =  credentials.get("project_id"),
    params = param
    )


from pandasai import SmartDataframe
from pandasai.llm import IBMwatsonx


# config for pandas.ai
llm = IBMwatsonx(
    model=models["llama"],
    api_key=credentials.get("apikey"),
    watsonx_url=credentials.get("url"),
    watsonx_project_id=credentials.get("project_id"),
    decoding_method= "greedy",
    temperature= 0.6, 
    min_new_tokens= 1000,
    max_new_tokens= 2500,
    stop_sequences= ['\nObservation', '\n\n']
)

if "__name__"=="__main__":
    response = llm.invoke("Explain polymorphsm in Java")
    print(response)


