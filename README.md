# AWS Lambda signed aiohttp requests

## What is this

Snippet of Python code to sign [aiohttp](https://github.com/aio-libs/aiohttp) requests using [SigV4](https://docs.aws.amazon.com/general/latest/gr/signature-version-4.html) for [invoking](https://docs.aws.amazon.com/lambda/latest/dg/API_Invoke.html) [AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html) functions concurrently.

## Why

This code will make your life a **lot easier** when you need to **send multiple Lambda invocation requests at once**, either synchronously or asynchronously. It uses the [`aiohttp`](https://github.com/aio-libs/aiohttp) library to send requests concurrently and automatically signs requests using your IAM credentials.

Both boto3 [invoke](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.invoke) and [invoke_async](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.invoke_async) APIs implement blocking code. Meaning: if you need to send multiple invocations at once, your Python code will send the first one, wait for it to respond, then send the second, and so on.

## How to

1. Import the `aiohttp_signed_lambda.py` snippet into your project.
1. Call the `invoke_all` function with the following arguments:
    * `requests` [_List_]: a list of _Dictionaries_ containing invocation arguments
    * `region` [_String_]: the AWS region where the invoked Lambda functions reside

## Example

```python
from signed_aiohttp_lambda import invoke_all


INVOCATION_ARGS = [
    {
        'function_name': 'my-lambda-function',
        'payload': {
            'hello': 'world',
        },
        'invocation_type': 'RequestResponse',  # Synchronous invocation
        'region': 'us-east-2',
    },
    {
        'function_name': 'another-lambda',
        'payload': {
            'task': 'execute xyz',
            'args': 123,
        },
        'invocation_type': 'Event',  # Asynchronous invocation
        'region': 'eu-west-1',
    },
    {
        'function_name': 'yet-another-lambda',
        'payload': {
            'foo': 'bar',
        },
        'invocation_type': 'DryRun',  # Validate parameter values & permissions
    },
]

# The region argument will be used for request invocations that do not
# specify one
responses = invoke_all(requests=INVOCATION_ARGS, region='us-east-1')
```
