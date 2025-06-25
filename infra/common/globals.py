# Copyright 2024 DataRobot, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enum import Enum
from typing import Literal

from pydantic import BaseModel

PROJECT_ROOT = __import__("pathlib").Path(__file__).resolve().parent.parent.parent.absolute()


class RuntimeEnvironment(BaseModel):
    name: str
    id: str


class GlobalRuntimeEnvironment(Enum):
    PYTHON_312_APPLICATION_BASE = RuntimeEnvironment(
        name="[DataRobot] Python 3.12",
        id="66d07fae0513a1edf18595bb",
    )
    PYTHON_311_NOTEBOOK_BASE = RuntimeEnvironment(
        name="[DataRobot] Python 3.11 Notebook Base Image",
        id="664388ff6d426582042bb3e4",
    )
    PYTHON_311_MODERATIONS = RuntimeEnvironment(
        name="[GenAI] Python 3.11 with Moderations", id="65f9b27eab986d30d4c64268"
    )
    PYTHON_312_MODERATIONS = RuntimeEnvironment(
        name="[GenAI] Python 3.12 with Moderations", id="67ab469cecdca772287de644"
    )
    PYTHON_39_CUSTOM_METRICS = RuntimeEnvironment(
        name="[DataRobot] Python 3.9 Custom Metrics Templates Drop-In",
        id="659bf1626529ceb502d12ae2",
    )
    PYTHON_311_NOTEBOOK_DROP_IN = RuntimeEnvironment(
        name="[DataRobot] Python 3.11 Notebook Drop-In", id="6583d56f5627082b3cff990e"
    )
    PYTHON_39_STREAMLIT = RuntimeEnvironment(
        name="[Experimental] Python 3.9 Streamlit", id="6542cd582a9d3d51bf4ac71e"
    )
    PYTHON_311_GENAI = RuntimeEnvironment(
        name="[DataRobot] Python 3.11 GenAI", id="64d2ba178dd3f0b1fa2162f0"
    )
    PYTHON_39_GENAI = RuntimeEnvironment(
        name="[DataRobot] Python 3.9 GenAI", id="64c964448dd3f0c07f47d040"
    )


CredentialType = Literal["azure", "aws", "google", "api"]


class LLMConfig(BaseModel):
    name: str
    credential_type: CredentialType


class GlobalLLM:
    """Available LLM configurations"""

    # Azure Models
    AZURE_OPENAI_GPT_3_5_TURBO = LLMConfig(
        name="azure-openai-gpt-3.5-turbo",
        credential_type="azure",
    )
    AZURE_OPENAI_GPT_3_5_TURBO_16K = LLMConfig(
        name="azure-openai-gpt-3.5-turbo-16k", credential_type="azure"
    )
    AZURE_OPENAI_GPT_4 = LLMConfig(name="azure-openai-gpt-4", credential_type="azure")
    AZURE_OPENAI_GPT_4_32K = LLMConfig(
        name="azure-openai-gpt-4-32k", credential_type="azure"
    )
    AZURE_OPENAI_GPT_4_TURBO = LLMConfig(
        name="azure-openai-gpt-4-turbo", credential_type="azure"
    )
    AZURE_OPENAI_GPT_4_O = LLMConfig(
        name="azure-openai-gpt-4-o", credential_type="azure"
    )
    AZURE_OPENAI_GPT_4_O_MINI = LLMConfig(
        name="azure-openai-gpt-4-o-mini", credential_type="azure"
    )

    # AWS Models
    AMAZON_TITAN = LLMConfig(name="amazon-titan", credential_type="aws")
    ANTHROPIC_CLAUDE_2 = LLMConfig(name="anthropic-claude-2", credential_type="aws")
    ANTHROPIC_CLAUDE_3_HAIKU = LLMConfig(
        name="anthropic-claude-3-haiku", credential_type="aws"
    )
    ANTHROPIC_CLAUDE_3_SONNET = LLMConfig(
        name="anthropic-claude-3-sonnet", credential_type="aws"
    )
    ANTHROPIC_CLAUDE_3_OPUS = LLMConfig(
        name="anthropic-claude-3-opus", credential_type="aws"
    )

    # Google Models
    GOOGLE_BISON = LLMConfig(name="google-bison", credential_type="google")
    GOOGLE_GEMINI_1_5_FLASH = LLMConfig(
        name="google-gemini-1.5-flash", credential_type="google"
    )
    GOOGLE_1_5_PRO = LLMConfig(name="google-gemini-1.5-pro", credential_type="google")

    # API Models
    DEPLOYED_LLM = LLMConfig(name="deployed-llm", credential_type="api")


class GlobalGuardrailTemplateName(str, Enum):
    CUSTOM_DEPLOYMENT = "Custom Deployment"
    FAITHFULNESS = "Faithfulness"
    PII_DETECTION = "PII Detection"
    PROMPT_INJECTION = "Prompt Injection"
    ROUGE_1 = "Rouge 1"
    SENTIMENT_CLASSIFIER = "Sentiment Classifier"
    STAY_ON_TOPIC_FOR_INPUTS = "Stay on topic for inputs"
    STAY_ON_TOPIC_FOR_OUTPUTS = "Stay on topic for output"
    TOKEN_COUNT = "Token Count"
    TOXICITY = "Toxicity"
