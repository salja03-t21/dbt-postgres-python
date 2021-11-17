# fal: do more with dbt
fal allows you to run python scripts directly from your [dbt](https://www.getdbt.com/) project.

With fal, you can:
- Send Slack notifications upon dbt model success or failure.
- Download dbt models into a Python context with a familiar syntax: `ref('my_dbt_model')`
- Use python libraries such as [`sklearn`](https://scikit-learn.org/) or [`prophet`](https://facebook.github.io/prophet/) to build more complex pipelines downstream of `dbt` models.

and more...

Check out our [Getting Started](#getting-started) guide to get a quickstart or play with [in-depth examples](#examples) to see how fal can help you get more done with dbt.

# Getting Started

## 1. Install fal
```bash
$ pip install fal
```

## 2. Go to your dbt directory
```bash
$ cd ~/src/my_dbt_project
```

## 3. Create a python script: `send_slack_message.py`
```python
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

CHANNEL_ID = os.getenv("SLACK_BOT_CHANNEL")
SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")

client = WebClient(token=SLACK_TOKEN)
message_text = f"Model: {context.current_model.name}. Status: {context.current_model.status}."

try:
    response = client.chat_postMessage(
        channel=CHANNEL_ID,
        text=message_text
    )
except SlackApiError as e:
    assert e.response["error"]
```
## 4. Add a `meta` section in your `schema.yml`
```yaml
models:
  - name: historical_ozone_levels
    description: Ozone levels
    config:
      materialized: table
    columns:
      - name: ozone_level
        description: Ozone level
      - name: ds
        description: Date
    meta:
      fal:
        scripts:
          - send_slack_message.py
```
## 5. Run `dbt` and `fal` consecutively
```bash
$ dbt run
# Your dbt models are ran

$ fal run
# Your python scripts are ran
```

# Examples
To explore what is possible with fal, take a look at the in-depth examples below. We will be adding more examples here over time:
- [Example 1: Send Slack notifications](docs/slack-example.md)
- [Example 2: Metric forecasting](docs/metric-forecast.md)
- [Example 3: Anomaly detection](docs/anomaly-detection.md)
- [Example 4: Sentiment analysis on support tickets](docs/sentiment-analysis.md)

# How it works?
`fal` is a command line tool that can read the state of your `dbt` project and help you run Python scripts after your `dbt run`s by leveraging the [`meta` config](https://docs.getdbt.com/reference/resource-configs/meta).

```yaml
models:
  - name: historical_ozone_levels
    ...
    meta:
      fal:
        scripts:
          - send_slack_message.py
          - another_python_script.py # will be ran after the first script
```

By default, the `fal run` command runs the Python scripts as a post-hook, **only** on the models that were ran on the last `dbt run` (So if you are using model selectors, `fal` will only run on the selected models). If you want to run all Python scripts regardless, you can use the `--all` flag with the `fal` CLI.

`fal` also provides useful helpers within the Python context to seamlessly interact with dbt models: `ref("my_dbt_model_name")` will pull a dbt model into your Python script as a [`pandas.DataFrame`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html).

# Concepts
## profile.yml and Credentials
`fal` integrates with `dbt`'s `profile.yml` file to access and read data from the data warehouse. Once you setup credentials in your `profile.yml` file for your existing `dbt` workflows anytime you use `ref` or `source` to create a dataframe `fal` authenticates using the credentials specified in the `profile.yml` file. 

## `meta` Syntax
```yaml
models:
  - name: historical_ozone_levels
    ...
    meta:
      fal:
        scripts:
          - send_slack_message.py
          - another_python_script.py # will be ran sequentially
```
Use the `fal` and `scripts` keys underneath the `meta` config to let `fal` CLI know where to look for the Python scripts. You can pass a list of scripts as shown above to run one or more scripts as a post-hook operation after a `dbt run`.

## Variables
Inside a Python script, you get access to some useful variables:

```python
# send_slack_message.py

# Refer to dbt models or sources by name. Returns a pandas.DataFrame.
ref('model_name')
source('source_name', 'table_name')

# Refer to a fal Context, which provides useful attributes about the dbt model in context.
context.current_model.name # Returns the current model name

context.current_model.meta # Returns the meta config of the current model as a Python dict
context.current_model.meta["owner"] # will return the "owner" key in the meta config

context.current_model.status # Returns the status of the last dbt run

ref(context.current_model.name) # Returns a pandas.DataFrame for the current model in context
```

## Lifecycle and State Management
By default, the `fal run` command runs the Python scripts as a post-hook, **only** on the models that were ran on the last `dbt run` (So if you are using model selectors, `fal` will only run on the selected models). 

If you want to run all Python scripts regardless, you can do so by using the `--all` flag with the `fal` CLI:

```bash
$ fal run --all
```

# Why are we building this?
We think `dbt` is great because it empowers data people to get more done with the tools that they are already familiar with. 

`dbt`'s SQL only design is powerful, but if you ever want to get out of SQL-land and connect to external services or get into Python-land for any reason, you will have a hard time. We built `fal` to enable Python workloads (sending alerts to Slack, building predictive models, pushing data to non-data warehose destinations and more) **right within `dbt`**.

This library will form the basis of our attempt to more comprehensively enable **data science workloads** downstream of dbt. And because having reliable data pipelines is the most important ingredient in building predictive analytics, we are building a library that integrates well with dbt.


# Have feedback or need help?
[Join us in #fal on Discord](https://discord.gg/ABbMkuBpNY)
