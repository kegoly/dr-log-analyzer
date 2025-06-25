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

from __future__ import annotations

import base64
import logging
import os
import sys
from io import StringIO

import datarobot as dr
import streamlit as st
from openai.types.chat.chat_completion_assistant_message_param import (
    ChatCompletionAssistantMessageParam,
)
from openai.types.chat.chat_completion_user_message_param import (
    ChatCompletionUserMessageParam,
)
from settings import app_settings
from streamlit.delta_generator import DeltaGenerator
from streamlit_theme import st_theme

sys.path.append("../")
from docsassist import predict
from docsassist.i18n import gettext

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)


DATAROBOT_ENDPOINT = os.getenv("DATAROBOT_ENDPOINT")
DATAROBOT_API_KEY = os.getenv("DATAROBOT_API_TOKEN")

st.set_page_config(
    page_title=app_settings.page_title, page_icon="./datarobot_favicon.png"
)

with open("./style.css") as f:
    css = f.read()

theme = st_theme()
logo = "./DataRobot_white.svg"
if theme and theme.get("base") == "light":
    logo = "./DataRobot_black.svg"

with open(logo) as f:
    svg = f.read()

st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

dr.Client(endpoint=DATAROBOT_ENDPOINT, token=DATAROBOT_API_KEY)


if "messages" not in st.session_state:
    st.session_state.messages = []

if "response" not in st.session_state:
    st.session_state.response = {}

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []


def render_svg(svg: str) -> None:
    """Renders the given svg string."""
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    st.write(html, unsafe_allow_html=True)


def process_uploaded_file(uploaded_file) -> str:
    """Process uploaded file and return its content as string."""
    try:
        if uploaded_file.type == "text/plain":
            # Read text file
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            content = stringio.read()
        elif uploaded_file.type in ["text/csv", "application/csv"]:
            # Read CSV file
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            content = stringio.read()
        else:
            # For other file types, try to read as text
            content = uploaded_file.getvalue().decode("utf-8")
        
        return f"📎 {uploaded_file.name}:\n{content}"
    except Exception as e:
        return f"📎 {uploaded_file.name}: Failed to read file. Error: {str(e)}"


def render_message(
    container: DeltaGenerator, message: str, is_user: bool = False
) -> None:
    message_role = "user" if is_user else "ai"
    message_label = gettext("User") if is_user else gettext("Assistant")
    
    # Handle file attachments in message
    if is_user and "📎" in message:
        # Split message into parts if it contains file content
        parts = message.split("📎")
        user_text = parts[0].strip() if parts[0].strip() else "File attached"
        
        container.markdown(
            f"""
        <div class="chat-message {message_role}-message">
            <div class="message-content">
                <span class="message-label"><b>{message_label}:</b></span>
                <span class="message-text">{user_text}</span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        
        # Show file contents in expandable sections
        for i, part in enumerate(parts[1:], 1):
            if part.strip():
                lines = part.strip().split('\n')
                filename = lines[0].split(':')[0] if ':' in lines[0] else f"File {i}"
                content = '\n'.join(lines[1:]) if len(lines) > 1 else "Unable to read content"
                
                with container.expander(f"📎 {filename}"):
                    st.text(content)
    else:
        container.markdown(
            f"""
        <div class="chat-message {message_role}-message">
            <div class="message-content">
                <span class="message-label"><b>{message_label}:</b></span>
                <span class="message-text">{message}</span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )


def render_answer_and_citations(
    container: DeltaGenerator, response: dict
) -> None:
    """Render the AI response."""
    try:
        # Extract completion from API response
        completion = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        completion = str(response)
    
    # Render the AI response
    render_message(container, completion, is_user=False)


def render_conversation_history(container: DeltaGenerator) -> None:
    container.subheader(gettext("Conversation History"))
    for message in st.session_state.messages[:-1]:  # Exclude the latest message
        render_message(container, message["content"], message["role"] == "user")
    st.markdown("---")


def main() -> None:
    render_svg(svg)
    st.title(app_settings.page_title)

    # File upload section
    uploaded_files = st.file_uploader(
        "📎 Select files to upload",
        accept_multiple_files=True,
        type=['txt', 'csv', 'log', 'json', 'md'],
        help="You can upload text files, CSV, log files, and other supported formats"
    )
    
    # Process uploaded files
    file_contents = []
    if uploaded_files:
        for uploaded_file in uploaded_files:
            content = process_uploaded_file(uploaded_file)
            file_contents.append(content)
        
        # Show uploaded files preview
        if file_contents:
            with st.expander(f"📎 Uploaded files ({len(file_contents)} file(s))"):
                for content in file_contents:
                    lines = content.split('\n')
                    filename = lines[0].replace('📎 ', '').split(':')[0]
                    st.write(f"**{filename}**")
                    # Show first few lines as preview
                    preview_lines = lines[1:4] if len(lines) > 1 else ["No content"]
                    for line in preview_lines:
                        if line.strip():
                            st.text(line[:100] + "..." if len(line) > 100 else line)
                    if len(lines) > 4:
                        st.text("...")
                    st.divider()

    chat_container = st.container()
    prompt_container = st.container()
    if st.session_state.messages:
        render_conversation_history(chat_container)
    answer_and_citations_placeholder = chat_container.container()
    if "prompt_sent" not in st.session_state:
        st.session_state.prompt_sent = False
    prompt = prompt_container.chat_input(
        placeholder=gettext("Your message"),
        key=None,
        max_chars=None,
        disabled=False,
        on_submit=None,
        args=None,
        kwargs=None,
    )

    if prompt and prompt.strip():
        st.session_state.prompt_sent = True
        
        # Combine prompt with file contents if files are uploaded
        full_message = prompt
        if file_contents:
            full_message = f"{prompt}\n\n" + "\n\n".join(file_contents)
        
        render_message(chat_container, full_message, True)
        with st.spinner(gettext("Getting AI response...")):
            response = predict.get_llm_completion(
                question=full_message,
                messages=st.session_state.messages,
            )
        st.session_state.response = response
        
        # Extract completion content from response
        try:
            completion_content = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            completion_content = str(response)
            
        st.session_state.messages.extend(
            [
                ChatCompletionUserMessageParam(content=full_message, role="user"),
                ChatCompletionAssistantMessageParam(
                    content=completion_content, role="assistant"
                ),
            ]
        )

        st.rerun()

    if st.session_state.prompt_sent:
        render_answer_and_citations(
            answer_and_citations_placeholder,
            st.session_state.response,
        )


if __name__ == "__main__":
    main()
