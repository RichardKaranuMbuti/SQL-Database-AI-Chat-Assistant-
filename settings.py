import os
from dataclasses import dataclass
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class WatsonxLLMConfig:
    model_id: str = "meta-llama/llama-3-1-70b-instruct"
    url: str = "https://eu-de.ml.cloud.ibm.com"
    apikey: str = os.getenv("apikey")
    project_id: str = os.getenv("project_id")
    decoding_method: str = "greedy"
    temperature: float = 0.6
    min_new_tokens: int = 1000
    max_new_tokens: int = 2500
    stop_sequences: List[str] = field(default_factory=lambda: ['\nObservation', '\n\n'])

    @property
    def credentials(self) -> Dict[str, str]:
        return {
            "url": self.url,
            "apikey": self.apikey,
            "project_id": self.project_id,
        }

    @property
    def params(self) -> Dict[str, Optional[str]]:
        return {
            "decoding_method": self.decoding_method,
            "temperature": self.temperature,
            "min_new_tokens": self.min_new_tokens,
            "max_new_tokens": self.max_new_tokens,
            "stop_sequences": self.stop_sequences,
        }


"""
config = WatsonxLLMConfig()
watsonx_llm = WatsonxLLM(
    model_id=config.model_id,
    url=config.credentials["url"],
    apikey=config.credentials["apikey"],
    project_id=config.credentials["project_id"],
    params=config.params,
)
"""

@dataclass
class AzureOpenAIChat35:
    azure_endpoint: str = os.getenv("CHAT_35_API_BASE")
    api_key: str = os.getenv("CHAT_35_API_KEY")
    api_version: str = os.getenv("CHAT_35_API_VERSION")
    azure_deployment: str = os.getenv("CHAT_35_DEPLOPMENT_NAME")


@dataclass
class AzureOpenAIChat4:
    azure_endpoint: str = os.getenv("CHAT_4_API_BASE")
    api_key: str = os.getenv("CHAT_4_API_KEY")
    api_version: str = os.getenv("CHAT_4_API_VERSION")
    azure_deployment: str = os.getenv("CHAT_4_DEPLOPMENT_NAME")

