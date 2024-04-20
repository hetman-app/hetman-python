from dotenv import dotenv_values
from hetman import HetmanFrame

from .hetman_workspaces import users_workspace

ENV_VARIABLES = dotenv_values('.env')

delete_user_frame = HetmanFrame(
    workspace=users_workspace,
    frame_uuid=ENV_VARIABLES['DELETE_USER_FRAME_UUID'],
    signature_secret=ENV_VARIABLES['DELETE_USER_SIGNATURE_SECRET']
)
