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

import textwrap
from typing import List, Sequence, Tuple

import datarobot as dr
import pulumi
import pulumi_datarobot as datarobot
from datarobot_pulumi_utils.schema.apps import ApplicationSourceArgs

from docsassist.i18n import LanguageCode, LocaleSettings
from infra.common.globals import GlobalRuntimeEnvironment
from infra.settings_main import PROJECT_ROOT, project_name

_application_path = PROJECT_ROOT / "frontend"

app_source_args = ApplicationSourceArgs(
    resource_name=f"Log Analyzer App Source [{project_name}]",
    base_environment_id=GlobalRuntimeEnvironment.PYTHON_312_APPLICATION_BASE.value.id,
).model_dump(mode="json", exclude_none=True)

app_resource_name: str = f"Log Analyzer Application [{project_name}]"


def ensure_app_settings(app_id: str) -> None:
    try:
        dr.client.get_client().patch(
            f"customApplications/{app_id}/",
            json={"allowAutoStopping": True},
        )
    except Exception:
        pulumi.warn("Patching app unsuccessful.")
    return


def ensure_app_source_settings(source_id: str, version_id: str) -> str:
    try:
        dr.client.get_client().patch(
            url=f"customApplicationSources/{source_id}/versions/{version_id}/",
            json={
                "resources": {
                    "sessionAffinity": True,
                    "resourceLabel": "cpu.xlarge",
                    "replicas": 2,
                }
            },
        )
    except dr.errors.ClientError:
        pulumi.warn("Patching app source unsuccessful.")
    return version_id


def _prep_metadata_yaml(
    runtime_parameter_values: Sequence[
        datarobot.ApplicationSourceRuntimeParameterValueArgs
        | datarobot.CustomModelRuntimeParameterValueArgs
    ],
) -> None:
    """Prepare metadata.yaml with runtime parameters if template exists"""
    metadata_template = _application_path / "metadata.yaml.jinja"
    if metadata_template.exists():
        from jinja2 import BaseLoader, Environment

        llm_runtime_parameter_specs = "\n".join(
            [
                textwrap.dedent(
                    f"""\
                - fieldName: {param.key}
                  type: {param.type}
            """
                )
                for param in runtime_parameter_values
            ]
        )
        with open(metadata_template) as f:
            template = Environment(loader=BaseLoader()).from_string(f.read())
        (_application_path / "metadata.yaml").write_text(
            template.render(
                additional_params=llm_runtime_parameter_specs,
            )
        )


def get_app_files(
    runtime_parameter_values: Sequence[
        datarobot.ApplicationSourceRuntimeParameterValueArgs
        | datarobot.CustomModelRuntimeParameterValueArgs,
    ],
) -> List[Tuple[str, str]]:
    _prep_metadata_yaml(runtime_parameter_values)
    
    # Get all files from application path
    source_files = [
        (str(f), str(f.relative_to(_application_path)))
        for f in _application_path.glob("**/*")
        if f.is_file()
    ]

    # Add docsassist files
    docsassist_path = PROJECT_ROOT / "docsassist"
    source_files.extend(
        [
            (str(docsassist_path / "__init__.py"), "docsassist/__init__.py"),
            (str(docsassist_path / "credentials.py"), "docsassist/credentials.py"),
            (str(docsassist_path / "deployments.py"), "docsassist/deployments.py"),
            (str(docsassist_path / "predict.py"), "docsassist/predict.py"),
            (str(docsassist_path / "schema.py"), "docsassist/schema.py"),
            (str(docsassist_path / "i18n.py"), "docsassist/i18n.py"),
        ]
    )

    # Add locale files if needed
    application_locale = LocaleSettings().app_locale
    if application_locale != LanguageCode.EN:
        source_files.append(
            (
                str(
                    docsassist_path
                    / "locale"
                    / application_locale
                    / "LC_MESSAGES"
                    / "base.mo"
                ),
                f"docsassist/locale/{application_locale}/LC_MESSAGES/base.mo",
            )
        )

    # Get all .py files from utils directory
    utils_files = [
        (str(PROJECT_ROOT / f"utils/{f.name}"), f"utils/{f.name}")
        for f in (PROJECT_ROOT / "utils").glob("*.py")
        if f.is_file()
    ]
    source_files.extend(utils_files)

    return source_files
