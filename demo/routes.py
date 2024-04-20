from flask import Blueprint, request
from hetman import HetmanAuth

from .hetman_frames import delete_user_frame

routes = Blueprint('routes', __name__)


@routes.route('/protected-endpoint', methods=['POST'])
@HetmanAuth.authorize_request(frame=delete_user_frame)
def routes_protected_endpoint():
    # Route completed a crucial task here that can only be accessed by authorized employees

    return "Success"


@routes.route('/protected-endpoint-raw', methods=['POST'])
def routes_protected_raw_endpoint():
    HetmanAuth(
        frame=delete_user_frame, incoming_request_data=request.get_json()
    ).authorize_func()

    # Route completed a crucial task here that can only be accessed by authorized employees

    return "Success"
