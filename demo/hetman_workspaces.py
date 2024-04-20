from dotenv import dotenv_values
from hetman import HetmanWorkspace

from .hetman_configs import general_hetman_config

ENV_VARIABLES = dotenv_values('.env')

users_workspace = HetmanWorkspace(
    api_key=ENV_VARIABLES['USERS_WORKSPACE_API_KEY'],
    api_key_secret=ENV_VARIABLES['USERS_WORKSPACE_API_KEY_SECRET'],
    workspace_uuid=ENV_VARIABLES['USERS_WORKSPACE_UUID'],
    base_api_endpoint=ENV_VARIABLES['DEMO_ENDPOINT'],
    config=general_hetman_config
)
