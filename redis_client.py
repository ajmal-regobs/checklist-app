import os
import time
import threading
import redis
import boto3
from botocore.signers import RequestSigner
from botocore.session import Session

REGION = os.environ["AWS_REGION"]
CLUSTER_NAME = os.environ["ELASTICACHE_CLUSTER_NAME"]
REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
IAM_USER = os.environ["REDIS_IAM_USER"]

TOKEN_TTL_SECONDS = 900


class IAMAuthTokenProvider:
    def __init__(self):
        self._lock = threading.Lock()
        self._token = None
        self._expires_at = 0
        self._session = Session()

    def get_token(self):
        with self._lock:
            now = time.time()
            if self._token and now < self._expires_at - 60:
                return self._token
            self._token = self._generate_token()
            self._expires_at = now + TOKEN_TTL_SECONDS
            return self._token

    def _generate_token(self):
        credentials = self._session.get_credentials()
        signer = RequestSigner(
            "elasticache",
            REGION,
            "elasticache",
            "v4",
            credentials,
            self._session.get_component("event_emitter"),
        )
        query = f"Action=connect&User={IAM_USER}"
        url = f"https://{CLUSTER_NAME}/?{query}"
        request_dict = {
            "method": "GET",
            "url": url,
            "body": {},
            "headers": {},
            "context": {},
        }
        signed_url = signer.generate_presigned_url(
            request_dict,
            operation_name="connect",
            expires_in=TOKEN_TTL_SECONDS,
            region_name=REGION,
        )
        return signed_url.removeprefix("https://")


_token_provider = IAMAuthTokenProvider()


def _credential_provider():
    return (IAM_USER, _token_provider.get_token())


def get_redis():
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        ssl=True,
        credential_provider=_CredentialProvider(),
        decode_responses=True,
    )


class _CredentialProvider(redis.CredentialProvider):
    def get_credentials(self):
        return _credential_provider()
