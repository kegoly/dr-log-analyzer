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

import os
import pathlib
import sys

import datarobot as dr
import pulumi
import pulumi_datarobot as datarobot

sys.path.append("..")

from datarobot_pulumi_utils.common import check_feature_flags
from datarobot_pulumi_utils.common.urls import get_deployment_url
from datarobot_pulumi_utils.pulumi.custom_model_deployment import CustomModelDeployment

from infra import (
    settings_generative,
    settings_keyword_guard, 
    settings_guardrails,
    settings_app_infra,
)
from infra.settings_global_model_guardrails import global_guardrails
from infra.settings_main import project_name
from infra.common.globals import GlobalRuntimeEnvironment, PROJECT_ROOT
from utils.credentials import get_credential_runtime_parameter_values, get_credentials
from utils.resources import app_env_name, llm_deployment_env_name
from utils.schema import AppInfra

check_feature_flags(pathlib.Path("feature_flag_requirements.yaml"))

# Create infrastructure configuration JSON
with open(PROJECT_ROOT / "frontend/app_infra.json", "w") as infra_selection:
    infra_selection.write(
        AppInfra(
            database="none",  # No database in simplified version
            llm=settings_generative.LLM.name,
        ).model_dump_json()
    )

if "DATAROBOT_DEFAULT_USE_CASE" in os.environ:
    use_case_id = os.environ["DATAROBOT_DEFAULT_USE_CASE"]
    pulumi.info(f"Using existing use case '{use_case_id}'")
    use_case = datarobot.UseCase.get(
        id=use_case_id,
        resource_name="Log Analyzer Use Case [PRE-EXISTING]",
    )
else:
    use_case = datarobot.UseCase(
        resource_name=f"Log Analyzer Use Case [{project_name}]",
        description="Use case for Log Analyzer application with guardrails",
    )

prediction_environment = datarobot.PredictionEnvironment(
    resource_name=f"Log Analyzer Prediction Environment [{project_name}]",
    platform=dr.enums.PredictionEnvironmentPlatform.DATAROBOT_SERVERLESS,
)

llm_credential = get_credentials(settings_generative.LLM)
llm_runtime_parameter_values = get_credential_runtime_parameter_values(
    llm_credential
)

# Create keyword guard deployment
keyword_guard_deployment = CustomModelDeployment(
    resource_name=f"Keyword Guard [{project_name}]",
    custom_model_args=settings_keyword_guard.custom_model_args,
    registered_model_args=settings_keyword_guard.registered_model_args,
    prediction_environment=prediction_environment,
    deployment_args=settings_keyword_guard.deployment_args,
)

# Create global guard deployments
global_guard_deployments = [
    datarobot.Deployment(
        registered_model_version_id=datarobot.get_global_model(
            name=guard.registered_model_name,
        ).version_id,
        prediction_environment_id=prediction_environment.id,
        use_case_ids=[use_case.id],
        **guard.deployment_args.model_dump(),
    )
    for guard in global_guardrails
]

all_guard_deployments = [keyword_guard_deployment] + global_guard_deployments

all_guardrails_configs = [
    settings_keyword_guard.custom_model_guard_configuration_args
] + [guard.custom_model_guard_configuration_args for guard in global_guardrails]

guard_configurations = [
    datarobot.CustomModelGuardConfigurationArgs(
        deployment_id=deployment.id,
        **guard_config_args.model_dump(mode="json", exclude_none=True),
    )
    for deployment, guard_config_args in zip(
        all_guard_deployments,
        all_guardrails_configs,
    )
] + settings_guardrails.guardrails

# Create playground
playground = datarobot.Playground(
    use_case_id=use_case.id,
    **settings_generative.playground_args,
)

# Create LLM blueprint  
llm_blueprint = datarobot.LlmBlueprint(
    playground_id=playground.id,
    **settings_generative.llm_blueprint_args.model_dump(),
)

# Create LLM custom model with guardrails
llm_custom_model = datarobot.CustomModel(
    **settings_generative.custom_model_args.model_dump(exclude_none=True),
    use_case_ids=[use_case.id],
    source_llm_blueprint_id=llm_blueprint.id,
    guard_configurations=guard_configurations,
    runtime_parameter_values=llm_runtime_parameter_values,
)

# Create LLM deployment
llm_deployment = CustomModelDeployment(
    resource_name=f"Log Analyzer LLM Deployment [{project_name}]",
    custom_model_version_id=llm_custom_model.version_id,
    registered_model_args=settings_generative.registered_model_args,
    prediction_environment=prediction_environment,
    deployment_args=settings_generative.deployment_args,
    use_case_ids=[use_case.id],
)

# Create application runtime parameters
app_runtime_parameters = [
    datarobot.ApplicationSourceRuntimeParameterValueArgs(
        key=llm_deployment_env_name,
        type="deployment",
        value=llm_deployment.id,
    ),
]

# Create application source with frontend files
app_source = datarobot.ApplicationSource(
    files=settings_app_infra.get_app_files(
        runtime_parameter_values=app_runtime_parameters
    ),
    runtime_parameter_values=app_runtime_parameters,
    **settings_app_infra.app_source_args,
)

app_source_version_id = pulumi.Output.all(app_source.id, app_source.version_id).apply(
    lambda args: settings_app_infra.ensure_app_source_settings(*args)
)

# Create application
app = datarobot.CustomApplication(
    resource_name=settings_app_infra.app_resource_name,
    source_version_id=app_source.version_id,
    use_case_ids=[use_case.id],
    external_access_enabled=True,
    external_access_recipients=["@datarobot.com"],
)

app.id.apply(settings_app_infra.ensure_app_settings)

# Exports - Main deployments
pulumi.export(llm_deployment_env_name, llm_deployment.id)
pulumi.export("KEYWORD_GUARD_DEPLOYMENT_ID", keyword_guard_deployment.id)
pulumi.export(app_env_name, app.id)

# Exports - Deployment URLs  
pulumi.export(settings_generative.deployment_args.resource_name, llm_deployment.id.apply(get_deployment_url))
pulumi.export(settings_keyword_guard.deployment_args.resource_name, keyword_guard_deployment.id.apply(get_deployment_url))
pulumi.export(settings_app_infra.app_resource_name, app.application_url)

for deployment, config in zip(global_guard_deployments, global_guardrails):
    pulumi.export(
        config.deployment_args.resource_name,
        deployment.id.apply(get_deployment_url),
    )
