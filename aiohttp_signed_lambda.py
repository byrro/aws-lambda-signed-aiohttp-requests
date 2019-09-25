'''
Credits to Mathew Marcus (2019)
https://www.mathewmarcus.com/blog/
http://archive.is/nXkCb
Small syntax and organization modifications were made to the original code.
'''
import asyncio
import json
import os
from typing import Dict, List, Optional
import urllib

import aiohttp
from botocore import session, awsrequest, auth


AWS_CREDENTIALS = session.Session().get_credentials()
LAMBDA_ENDPOINT = 'https://lambda.{region}.amazonaws.com/2015-03-31/functions'


def sign_headers(*, url: str, payload: Dict, invocation_type: str):
    '''Sign AWS API request headers'''
    segments = urllib.parse.urlparse(url).netloc.split('.')
    service = segments[0]
    region = segments[1]

    request = awsrequest.AWSRequest(
        method='POST',
        url=url,
        data=json.dumps(payload),
        headers={
            'X-Amz-Invocation-Type': invocation_type,
        }
    )

    auth.SigV4Auth(AWS_CREDENTIALS, service, region).add_auth(request)

    return dict(request.headers.items())


async def invoke(
        *,
        url: str,
        payload: Dict,
        invocation_type='RequestResponse',  # Options: 'Event', 'DryRun',
        session,
    ):
    '''Invoke a Lambda function'''
    signed_headers = sign_headers(
        url=url,
        payload=payload,
        invocation_type=invocation_type,
    )

    async with session.post(url, json=payload, headers=signed_headers) \
            as response:
        return await response.json()


def run_invocations(*, requests: List, base_url: str, default_region: Optional(str), session):
    for request in requests:
        if not request.get('region') and not default_region:
            raise ValueError(
                'Must provide a region, either in the invocation arguments or'
                'as a default region when calling invoke_all'
            )

        region = request.get('region') if type(request['region']) is str else \
            default_region

        base_url = LAMBDA_ENDPOINT.format(region=region)

        url = os.path.join(base_url, request['function_name'], 'invocations')

        yield invoke(
            url=url,
            payload=request['payload'],
            invocation_type=request['invocation_type'],
            session=session,
        )


def invoke_all(*, requests: List, region: Optional(str = 'us-east-1')):
    async def wrapper():
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            invocations = run_invocations(
                requests=requests,
                default_region=region,
                session=session,
            )

            return await asyncio.gather(*invocations)

    loop = asyncio.get_event_loop()

    results = loop.run_until_complete(wrapper())

    return results
