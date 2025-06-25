# Log Analyzer Assistant

The log analyzer assistant is an easily customizable recipe for building a chat-powered assistant for analyzing logs and documents. 

In addition to creating a hosted, shareable user interface, the log analyzer assistant provides:

* Business logic and LLM-based guardrails.
* GenAI-focused [custom metrics][custom-metrics].
* DataRobot MLOps hosting, monitoring, and governing the individual back-end deployments.

> [!WARNING]
> Application templates are intended to be starting points that provide guidance on how to develop, serve, and maintain AI applications.
> They require a developer or data scientist to adapt and modify them for their business requirements before being put into production.

![Using the Log Analyzer Assistant](https://s3.amazonaws.com/datarobot_public/drx/recipe_gifs/launch_gifs/log-analyzer-small.gif)

[custom-metrics]: https://docs.datarobot.com/en/docs/workbench/nxt-console/nxt-monitoring/nxt-custom-metrics.html

## Table of contents
1. [Setup](#setup)
2. [Architecture overview](#architecture-overview)
3. [Why build AI Apps with DataRobot app templates?](#why-build-ai-apps-with-datarobot-app-templates)
3. [Make changes](#make-changes)
   - [Change the LLM](#change-the-llm)
   - [Custom front-end](#fully-custom-front-end)
4. [Share results](#share-results)
5. [Delete all provisioned resources](#delete-all-provisioned-resources)
6. [Setup for advanced users](#setup-for-advanced-users)
7. [Data Privacy](#data-privacy)


## Setup

> [!IMPORTANT]
> If you are running this template in a DataRobot codespace, `pulumi` is already configured and the repo is automatically cloned;
> skip to **Step 3**.
1. If `pulumi` is not already installed, install the CLI following instructions [here](https://www.pulumi.com/docs/iac/download-install/). 
   After installing for the first time, restart your terminal and run:
   ```bash
   pulumi login --local  # omit --local to use Pulumi Cloud (requires separate account)
   ```

2. Clone the template repository.

   ```bash
   git clone https://github.com/datarobot-community/dr-log-analyzer.git
   cd dr-log-analyzer
   ```

3. Rename the file `.env.template` to `.env` in the root directory of the repo and populate your credentials.
   This template is pre-configured to use an Azure OpenAI endpoint. If you wish to use a different LLM provider, modifications to the code will be [necessary](#change-the-llm).

   Please refer to the documentation inside `.env.template`

4. In a terminal, run:
   ```bash
   python quickstart.py YOUR_PROJECT_NAME  # Windows users may have to use `py` instead of `python`
   ```
   Python 3.9+ is required.

Advanced users desiring control over virtual environment creation, dependency installation, environment variable setup,
and `pulumi` invocation see [the advanced setup instructions](#setup-for-advanced-users).


## Architecture overview

![Log Analyzer architecture](https://s3.amazonaws.com/datarobot_public/drx/recipe_gifs/log_analyzer_architecture.svg)

App templates contain two families of complementary logic. For Log Analyzer you can [opt-in](#make-changes) to a fully custom frontend or utilize DR's off the shelf offerings:

- **AI logic**: Necessary to service AI requests and produce predictions and completions.
  ```
  deployment_keyword_guard/  # Keyword guard scoring logic
  ```
- **App Logic**: Necessary for user consumption; whether via a hosted front-end or integrating into an external consumption layer.
  ```
  frontend/  # Streamlit frontend (DIY frontend)
  docsassist/  # App business logic & runtime helpers (DIY front-end)
  ```
- **Operational Logic**: Necessary to activate DataRobot assets.
  ```
  infra/  # Settings for resources and assets to be created in DataRobot
  infra/__main__.py  # Pulumi program for configuring DataRobot to serve and monitor AI and App logic
  ```

## Why build AI Apps with DataRobot app templates?

App Templates transform your AI projects from notebooks to production-ready applications. Too often, getting models into production means rewriting code, juggling credentials, and coordinating with multiple tools & teams just to make simple changes. DataRobot's composable AI apps framework eliminates these bottlenecks, letting you spend more time experimenting with your ML and app logic and less time wrestling with plumbing and deployment.

- Start building in minutes: Deploy complete AI applications instantly, then customize the AI logic or the front-end independently (no architectural rewrites needed).
- Keep working your way: Data scientists keep working in notebooks, developers in IDEs, and configs stay isolated. Update any piece without breaking others.
- Iterate with confidence: Make changes locally and deploy with confidence. Spend less time writing and troubleshooting plumbing and more time improving your app.

Each template provides an end-to-end AI architecture, from raw inputs to deployed application, while remaining highly customizable for specific business requirements.

## Make changes

### Change the LLM

1. Modify the `LLM` setting in `infra/settings_generative.py` by changing `LLM=GlobalLLM.AZURE_OPENAI_GPT_4_O_MINI` to any other LLM from the `GlobalLLM` object. 
     - Trial users: Please set `LLM=GlobalLLM.AZURE_OPENAI_GPT_4_O_MINI` since GPT-4o is not supported in the trial. Use the `OPENAI_API_DEPLOYMENT_ID` in `.env` to override which model is used in your azure organisation. You'll still see GPT 4o-mini in the playground, but the deployed app will use the provided azure deployment.  
2. To use an existing TextGen model or deployment:
      - In `infra/settings_generative.py`: Set `LLM=GlobalLLM.DEPLOYED_LLM`.
      - In `.env`: Set either the `TEXTGEN_REGISTERED_MODEL_ID` or the `TEXTGEN_DEPLOYMENT_ID`
      - In `.env`: Set `CHAT_MODEL_NAME` to the model name expected by the deployment (e.g. "claude-3-7-sonnet-20250219" for an anthropic deployment, "datarobot-deployed-llm" for NIM models )
3. In `.env`: If not using an existing TextGen model or deployment, provide the required credentials dependent on your choice.
4. Run `pulumi up` to update your stack (Or rerun your quickstart).
      ```bash
      source set_env.sh  # On windows use `set_env.bat`
      pulumi up
      ```

> **⚠️ Availability information:**  
> Using a NIM model requires custom model GPU inference, a premium feature. You will experience errors by using this type of model without the feature enabled. Contact your DataRobot representative or administrator for information on enabling this feature.

### Fully custom front-end

1. Run `pulumi up` to update your stack with the example custom Streamlit frontend:
   ```bash
   source set_env.sh  # On windows use `set_env.bat`
   pulumi up
   ```
2. After provisioning the stack at least once, you can also edit and test the Streamlit
   front-end locally using `streamlit run app.py` from the `frontend/` directory (don't
   forget to initialize your environment using `set_env`).
   ```bash
   source set_env.sh  # On windows use `set_env.bat`
   cd frontend
   streamlit run app.py
   ```
## Share results

1. Log into the DataRobot application.
2. Navigate to **Registry > Applications**.
3. Navigate to the application you want to share, open the actions menu, and select **Share** from the dropdown.

## Delete all provisioned resources
```bash
pulumi down
```

## Setup for advanced users
For manual control over the setup process adapt the following steps for MacOS/Linux to your environent:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
source set_env.sh
pulumi stack init YOUR_PROJECT_NAME
pulumi up
```
e.g. for Windows/conda/cmd.exe this would be:
```bash
conda create --prefix .venv pip
conda activate .\.venv
pip install -r requirements.txt
set_env.bat
pulumi stack init YOUR_PROJECT_NAME
pulumi up
```
For projects that will be maintained, DataRobot recommends forking the repo so upstream fixes and improvements can be merged in the future.

## Data Privacy
Your data privacy is important to us. Data handling is governed by the DataRobot [Privacy Policy](https://www.datarobot.com/privacy/), please review before using your own data with DataRobot.
