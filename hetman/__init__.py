#      @@
#  @@ @@@@ @@
#  @@@@@@@@@@
#    @@@@@@
#     @@@@
#    @@@@@@
#     @@@@       ┣┓┏┓╋┏┳┓┏┓┏┓ ┏┓┏┓┏┓       Copyright © 2024 yaria.pl
#     @@@@       ┛┗┗ ┗┛┗┗┗┻┛┗•┗┻┣┛┣┛       All rights reserved.
#     @@@@                      ┛ ┛
#  @@@@@@@@@@
#  @@@@@@@@@@

import hashlib
import hmac
import json
import re
from copy import deepcopy
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, List, Optional

import requests

from ._exceptions import (
    FailedRequest, FrameUUIDDismatch, InvalidAccessToken, InvalidApiKey,
    InvalidBaseApiEndpoint, InvalidSignature, InvalidWorkspaceUUID, MissingData,
    NotFoundInAuthorizedMembers
)

# Default error messages for aborting requests

DEFAULT_ABORT_MESSAGES = {
    'InvalidSignature':
        "You are not authorized. Bad signature.",
    'MissingData':
        "Incomplete authorization request.",
    'FrameUUIDDismatch':
        "Request sent to bad endpoint.",
    'NotFoundInAuthorizedMembers':
        "You are not authorized. You are not in the authorized members list.",
    'InvalidAccessToken':
        "You are not authorized. Access token dismatch."
}


@dataclass
class HetmanBaseConfig:
    """
    Configuration settings for Hetman framework.

    Attributes:
        incoming_data_getter (Callable[[], dict]): A callable that retrieves incoming request data.
        abort_function (Callable[[dict], Any]): A callable function to handle aborting the request.
        abort_messages (dict): A dictionary containing default abort messages for various exceptions.
        own_functions_to_run (List[Callable]): A list of functions to run before Hetman authorization.
    """

    incoming_data_getter: Callable[[], dict]
    abort_function: Callable[[dict], Any]
    abort_messages: dict = field(default_factory=lambda: DEFAULT_ABORT_MESSAGES)
    own_functions_to_run: List[Callable] = field(default_factory=lambda: [])


class HetmanWorkspace:
    def __init__(
        self,
        api_key: str,
        api_key_secret: str,
        workspace_uuid: str,
        config: HetmanBaseConfig,
        base_api_endpoint:
        str = 'https://hetman.app/api/project/workspaces/internal'
    ) -> None:
        """
        Initializes a HetmanWorkspace instance.

        Args:
            api_key (str): The workspace API key for authentication.
            api_key_secret (str): The secret key associated with the workspace API key.
            workspace_uuid (str): The UUID of the workspace.
            config (HetmanBaseConfig): Configuration settings for the workspace.
            base_api_endpoint (str, optional): The base URL for the API endpoint. Defaults to 'https://hetman.app/api/project/workspaces/internal'.

        Raises:
            InvalidApiKey: If the provided API key is invalid.
            InvalidWorkspaceUUID: If the provided workspace UUID is invalid.
            InvalidBaseApiEndpoint: If the provided base API endpoint is invalid.
        """

        self.api_key = api_key
        self.api_key_secret = api_key_secret
        self.base_api_endpoint = base_api_endpoint
        self.workspace_uuid = workspace_uuid
        self.config = config
        self._authorized_workspace_members = {}

        self.__validate_init_args()

    def get_authorized_workspace_members(self):
        """
        Retrieves authorized workspace members from the API and caches the result.
        
        Raises:
            FailedRequest: If the request to fetch authorized workspace members fails.
        """

        data = {
            'workspaceUUID': self.workspace_uuid,
            'apiKey': self.api_key,
            'apiKeySecret': self.api_key_secret
        }

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        api_endpoint = f"{self.base_api_endpoint}/authorized-workspace-members"

        response = requests.post(url=api_endpoint, data=data, headers=headers)

        if response.status_code != 200:
            raise FailedRequest(
                f"Failed to fetch authorized workspace members. Status code: {response.status_code}"
            )

        if response.headers.get('Content-Type') != 'application/json':
            raise FailedRequest("Response content type is not JSON.")

        self._authorized_workspace_members = response.json().get('frames', {})

    @property
    def authorized_workspace_members(self):
        """
        Property to access authorized workspace members.

        Returns:
            dict: A dictionary containing authorized workspace members.
        """

        if not self._authorized_workspace_members:
            self.get_authorized_workspace_members()

        return self._authorized_workspace_members

    def __validate_init_args(self):
        """
        Validates the initialization arguments.
        
        Raises:
            InvalidApiKey: If the API key is invalid.
            InvalidWorkspaceUUID: If the workspace UUID is invalid.
            InvalidBaseApiEndpoint: If the base API endpoint is invalid.
        """

        uuid_regex = r'^[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}$'

        if not re.match(uuid_regex, self.api_key):
            raise InvalidApiKey(self.api_key)

        if not re.match(uuid_regex, self.workspace_uuid):
            raise InvalidWorkspaceUUID(self.workspace_uuid)

        if not re.match(
            r"(www|http:|https:)+[^\s]+[\w]", self.base_api_endpoint
        ):
            raise InvalidBaseApiEndpoint(self.base_api_endpoint)


@dataclass
class HetmanFrame:
    """
    Represents a frame within the Hetman framework.

    Attributes:
        workspace (HetmanWorkspace): The workspace to which the frame belongs.
        frame_uuid (str): The UUID of the frame.
        signature_secret (str): The secret key used for signature generation.
        config (Optional[HetmanBaseConfig]): Configuration settings for the frame.
    """

    workspace: HetmanWorkspace
    frame_uuid: str
    signature_secret: str
    config: Optional[HetmanBaseConfig] = None

    def __post_init__(self):
        if self.config is None:
            self.config = self.workspace.config if self.workspace else None


class HetmanAuth:
    def __init__(self, frame: HetmanFrame, incoming_request_data: dict) -> None:
        """
        Initializes a HetmanAuth instance.

        Args:
            frame (HetmanFrame): The frame to authenticate.
            incoming_request_data (dict): Incoming request data for authentication.
        """

        self.frame = frame
        self.incoming_request_data = incoming_request_data

    @staticmethod
    def authorize_request(frame: HetmanFrame):
        """
        Decorator for authorizing requests.

        Args:
            frame (HetmanFrame): The frame to authorize.

        Returns:
            Callable: Decorator function.
        """
        def decorator(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                incoming_request_data = frame.config.incoming_data_getter()

                try:
                    HetmanAuth(
                        frame=frame,
                        incoming_request_data=incoming_request_data
                    ).authorize_func()
                except Exception as error:
                    exception_type = type(error).__name__

                    abort_message = frame.config.abort_messages.get(
                        exception_type
                    )

                    if not abort_message:
                        abort_message = DEFAULT_ABORT_MESSAGES.get(
                            exception_type
                        )

                        if not abort_message:
                            abort_message = 'You are not authorized. Unknown error.'

                    return frame.config.abort_function(
                        message=abort_message, code=401
                    )

                response = f(*args, **kwargs)

                return response

            return wrapped

        return decorator

    def authorize_func(self):
        """
        Performs authorization checks.
        
        Raises:
            MissingData: If required data is missing.
            FrameUUIDDismatch: If the frame UUID mismatches.
            InvalidAccessToken: If the access token is invalid.
            InvalidSignature: If the signature is invalid.
        """

        for func in self.frame.config.own_functions_to_run:
            if callable(func):
                func()

        self.preflight()
        self.check_signature()
        self.check_access_token()

    def preflight(self):
        """
        Checks preflight conditions.

        Raises:
            MissingData: If required data is missing.
            FrameUUIDDismatch: If the frame UUID mismatches.
        """

        frame_uuid_from_request = self.incoming_request_data.get(
            'authorization', {}
        ).get('frameUUID')

        if not frame_uuid_from_request:
            raise MissingData(missing='frameUUID in authorization')

        if self.frame.frame_uuid != frame_uuid_from_request:
            raise FrameUUIDDismatch(
                invalid_frame_uuid=frame_uuid_from_request,
                valid_frame_uuid=self.frame.frame_uuid
            )

    def check_access_token(self):
        """
        Checks the validity of the access token.

        Raises:
            MissingData: If required data is missing.
            NotFoundInAuthorizedMembers: If the workspace member is not found in authorized members.
            InvalidAccessToken: If the access token is invalid.
        """

        auth_data = self.incoming_request_data.get('authorization', {})

        workspace_member_from_request = auth_data.get('workspaceMemberUUID')

        if not workspace_member_from_request:
            raise MissingData(
                missing='workspaceMemberUUID is missing in authorization data.'
            )

        if not isinstance(workspace_member_from_request, str):
            raise TypeError('workspaceMemberUUID should be a string')

        access_token_from_request = auth_data.get('accessToken')

        if not access_token_from_request:
            raise MissingData(
                missing='accessToken is missing in authorization data.'
            )

        if not isinstance(access_token_from_request, str):
            raise TypeError('accessToken should be a string')

        authorized_workspace_members = self.frame.workspace.authorized_workspace_members

        frame_members = authorized_workspace_members.get(
            self.frame.frame_uuid, {}
        ).get('authorized_members', {})

        correct_workspace_member_access_token_hash = frame_members.get(
            workspace_member_from_request
        )

        if not correct_workspace_member_access_token_hash:
            raise NotFoundInAuthorizedMembers(workspace_member_from_request)

        access_token_from_request_hash = hashlib.sha512(
            access_token_from_request.encode()
        ).hexdigest()

        if correct_workspace_member_access_token_hash != access_token_from_request_hash:
            raise InvalidAccessToken(workspace_member_from_request)

    def check_signature(self):
        """
        Checks the validity of the request signature.

        Raises:
            MissingData: If required data is missing.
            InvalidSignature: If the signature is invalid.
        """

        signature_from_request = self.incoming_request_data.get('signature')

        if not signature_from_request:
            raise MissingData('Signature is missing.')

        incoming_request_data = deepcopy(self.incoming_request_data)

        if not isinstance(signature_from_request, str):
            raise TypeError('signature should be a string')

        del incoming_request_data['signature']

        json_dumped_data = json.dumps(
            incoming_request_data, separators=(',', ':'), ensure_ascii=False
        )

        correct_signature = hmac.new(
            self.frame.signature_secret.encode(), json_dumped_data.encode(),
            hashlib.sha512
        ).hexdigest()

        if correct_signature != signature_from_request:
            raise InvalidSignature(signature_from_request, correct_signature)
