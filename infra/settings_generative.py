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

import datarobot as dr
import pulumi
import pulumi_datarobot as datarobot

from docsassist.schema import TARGET_COLUMN_NAME
from infra.common.globals import GlobalLLM
from infra.common.schema import (
    CustomModelArgs,
    DeploymentArgs,
    LLMBlueprintArgs,
    PlaygroundArgs,
    RegisteredModelArgs,
)
from infra.common.stack import project_name
from infra.settings_main import (
    runtime_environment_moderations,
    default_prediction_server_id,
)

LLM = GlobalLLM.AZURE_OPENAI_GPT_4_O

system_prompt = """\
You are a helpful assistant. Respond to user questions in a helpful and informative manner.
"""

playground_args = {
    "resource_name": f"Log Analyzer Playground [{project_name}]",
}

llm_blueprint_args = LLMBlueprintArgs(
    resource_name=f"Log Analyzer LLM Blueprint [{project_name}]",
    llm_id=LLM.name,
    llm_settings={
        "max_completion_length": 512,
        "system_prompt": system_prompt,
    },
)

custom_model_args = CustomModelArgs(
    resource_name=f"Log Analyzer Custom Model [{project_name}]",
    name="Log Analyzer Assistant",
    target_name=TARGET_COLUMN_NAME,
    target_type=dr.enums.TARGET_TYPE.TEXT_GENERATION,
    base_environment_id=runtime_environment_moderations.id,
    opts=pulumi.ResourceOptions(delete_before_replace=True),
)

registered_model_args = RegisteredModelArgs(
    resource_name=f"Log Analyzer Registered Model [{project_name}]",
)

deployment_args = DeploymentArgs(
    resource_name=f"Log Analyzer Deployment [{project_name}]",
    label=f"Log Analyzer Deployment [{project_name}]",
    association_id_settings=datarobot.DeploymentAssociationIdSettingsArgs(
        column_names=["association_id"],
        auto_generate_id=False,
        required_in_prediction_requests=True,
    ),
    predictions_settings=(
        None
        if default_prediction_server_id
        else datarobot.DeploymentPredictionsSettingsArgs(min_computes=0, max_computes=1)
    ),
    predictions_data_collection_settings=datarobot.DeploymentPredictionsDataCollectionSettingsArgs(
        enabled=True,
    ),
)
