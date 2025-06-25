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

import logging
import requests
import json

import datarobot as dr
import streamlit as st
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam

from docsassist.deployments import LLMDeployment

logger = logging.getLogger(__name__)


def get_rag_completion(question: str, messages: list[ChatCompletionMessageParam]) -> dict:
    """
    Send a prompt to the DataRobot Chat API and return the response
    
    Args:
        question (str): The user's question
        messages (list): Previous conversation messages
        
    Returns:
        dict: Response from the DataRobot Chat API
    """
    # Combine previous messages with the new question
    all_messages = []
    for msg in messages:
        all_messages.append({"role": msg["role"], "content": msg["content"]})
    
    all_messages.append({"role": "user", "content": question})
    
    # Request data for chat completions API
    data = {
        "model": "deployed-llm",
        "messages": all_messages
    }

    try:
        deployment_id = LLMDeployment().id
    except Exception as e:
        st.error(f"Failed to retrieve deployment ID: {str(e)}")
        raise

    try:
        client = dr.Client()
        base_url = client.endpoint
        
        # Retrieve deployment information
        url = f"{base_url}/deployments/{deployment_id}/chat/completions"
        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {client.token}"
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code != 200:
            raise Exception(
                f"DataRobot API Error: {response.status_code} - {response.text}")
        
        return response.json()

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        raise
