from flask import abort, request
from hetman import HetmanBaseConfig

general_hetman_config = HetmanBaseConfig(
    incoming_data_getter=lambda: request.get_json(),
    abort_function=lambda **kwargs:
    abort(kwargs.get('code'), kwargs.get('message'))
)
