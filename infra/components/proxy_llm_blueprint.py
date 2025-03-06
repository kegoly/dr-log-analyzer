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

from typing import Any, Optional

import datarobot as dr
import pulumi
import pulumi_datarobot as datarobot

from infra.common.schema import LLMSettings, VectorDatabaseSettings


class ProxyLLMBlueprint(pulumi.ComponentResource):
    @staticmethod
    def _get_column_names(
        proxy_llm_deployment_id: str,
        prompt_column_name: str | None = None,
    ) -> tuple[str, str]:
        try:
            deployment = dr.Deployment.get(deployment_id=proxy_llm_deployment_id)
        except Exception as e:
            raise ValueError("Couldn't find deployment ID") from e
        if deployment.model is None:
            raise ValueError("Deployment model is not set")

        target_column_name = deployment.model["target_name"]
        if target_column_name is None:
            raise ValueError("Target column name is not set")

        if prompt_column_name is None:
            if (
                "prompt" not in deployment.model
                or deployment.model.get("prompt") is None
            ):
                pulumi.warn(
                    "Couldn't infer prompt column name of the textgen deployment. Using default 'promptText'."
                )
            prompt_column_name = str(deployment.model.get("prompt", "promptText"))

        return (prompt_column_name, target_column_name)

    def __init__(
        self,
        resource_name: str,
        proxy_llm_deployment_id: pulumi.Output[str],
        use_case_id: pulumi.Output[str],
        playground_id: pulumi.Output[str],
        llm_id: str,
        llm_settings: LLMSettings,
        vector_database_settings: VectorDatabaseSettings,
        vector_database_id: pulumi.Output[str] | None = None,
        prompt_column_name: str | None = None,
        opts: Optional[pulumi.ResourceOptions] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            "custom:datarobot:ProxyLLMBlueprint", resource_name, None, opts
        )

        column_names = proxy_llm_deployment_id.apply(
            lambda id: self._get_column_names(
                proxy_llm_deployment_id=id,
                prompt_column_name=prompt_column_name,
            )
        )

        if isinstance(llm_settings, dict):
            llm_settings = LLMSettings(**llm_settings)
        if isinstance(vector_database_settings, dict):
            vector_database_settings = VectorDatabaseSettings(
                **vector_database_settings
            )
        self.llm_validation = datarobot.CustomModelLlmValidation(
            resource_name=f"{resource_name}-validation",
            deployment_id=proxy_llm_deployment_id,
            prompt_column_name=column_names[0],
            target_column_name=column_names[1],
            use_case_id=use_case_id,
        )
        self.llm_blueprint = datarobot.LlmBlueprint(
            resource_name=resource_name,
            custom_model_llm_settings=datarobot.LlmBlueprintCustomModelLlmSettingsArgs(
                system_prompt=llm_settings.system_prompt,
                validation_id=self.llm_validation.id,
            ),
            llm_id=llm_id,
            playground_id=playground_id,
            vector_database_id=vector_database_id,
            vector_database_settings=vector_database_settings.model_dump(),
        )

        self.register_outputs(
            {
                "llm_validation_id": self.llm_validation.id,
                "id": self.llm_blueprint.id,
            }
        )

    @property
    @pulumi.getter(name="id")
    def id(self) -> pulumi.Output[str]:
        """
        The ID of the latest Custom Model version.
        """
        return self.llm_blueprint.id
