# Copyright 2024 DataRobot, Inc.

from datarobot_pulumi_utils.schema.custom_models import (
    CustomModelArgs,
    DeploymentArgs,
    RegisteredModelArgs,
)
from datarobot_pulumi_utils.schema.llms import LLMBlueprintArgs
from datarobot_pulumi_utils.schema.apps import ApplicationSourceArgs

# PlaygroundArgs may not be available in this version, so we'll use dict instead
PlaygroundArgs = dict

__all__ = [
    "CustomModelArgs",
    "DeploymentArgs", 
    "RegisteredModelArgs",
    "LLMBlueprintArgs",
    "PlaygroundArgs",
    "ApplicationSourceArgs",
]
