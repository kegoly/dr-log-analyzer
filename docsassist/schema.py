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

from typing import Any, Dict

from pydantic import BaseModel


PROMPT_COLUMN_NAME: str = "promptText"
TARGET_COLUMN_NAME: str = "resultText"


class Reference(BaseModel):
    content: str
    link: str | None = None
    metadata: dict[str, Any]


class DocumentModel(BaseModel):
    page_content: str
    metadata: Dict[str, Any] = {}
