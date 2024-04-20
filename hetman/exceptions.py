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


class InvalidApiKey(Exception):
    def __init__(self, api_key: str):
        super().__init__(f'API Key must be a UUID. Invalid value: "{api_key}"')


class InvalidWorkspaceUUID(Exception):
    def __init__(self, workspace: str):
        super().__init__(f'Invalid workspace UUID "{workspace}"')


class InvalidBaseApiEndpoint(Exception):
    def __init__(self, api_endpoint: str) -> None:
        super().__init__(
            f'Base API Endpoint must be a URL. Invalid value: "{api_endpoint}"'
        )


class FailedRequest(Exception):
    def __init__(self, response, message: str = ''):
        super().__init__(
            f'Request has failed. response="{response.text}"; message={message};'
        )


class InvalidSignature(Exception):
    def __init__(self, invalid_signature: str, valid_signature: str):
        super().__init__(
            f'Signature in the request is invalid. invalid_signature={invalid_signature}; valid_signature={valid_signature};'
        )


class MissingData(Exception):
    def __init__(self, missing: str):
        super().__init__(f'Missing data in the request. missing={missing}')


class FrameUUIDDismatch(Exception):
    def __init__(self, invalid_frame_uuid: str, valid_frame_uuid: str):
        super().__init__(
            f'The request from the user was directed to the wrong frame UUID (Authorization should be for a different frame). invalid_frame_uuid={invalid_frame_uuid}; valid_frame_uuid={valid_frame_uuid};'
        )


class NotFoundInAuthorizedMembers(Exception):
    def __init__(self, workspace_member_from_request: str):
        super().__init__(
            f'Workspace member not fouond in the authorized members. workspace_member={workspace_member_from_request};'
        )


class InvalidAccessToken(Exception):
    def __init__(self, workspace_member_from_request: str):
        super().__init__(
            f'Invalid access token. workspace_member={workspace_member_from_request};'
        )
