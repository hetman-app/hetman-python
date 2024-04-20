<p align="center">
  <img src="https://raw.githubusercontent.com/hetman-app/.github/main/brand.svg" width="50" alt="hetman-logo">
</p>

---

*"Give yourself a break during the creation of the front-end administrative panel, utilize our services, and let yourself be captivated by the endless possibilities"* - hetman.app

Hetman is a Python framework created to offer secure authentication features for your application. This Python package includes integration with [hetman.app](https://hetman.app/) and handles authorization to guarantee your application's security.

***Our package is compatible with any Python web framework thanks to its dynamic functions. Take a look below. While we provide examples for Flask, you can use Hetman in any framework.***

## Installation

Hetman can be easily installed via pip:

```bash
pip install hetman
```

## Usage

### Configuration

Before using Hetman, you need to configure it with appropriate settings. The `HetmanBaseConfig` class allows you to define various configuration options for your workspace and frame.

```python
from hetman import HetmanBaseConfig

# Define a function to retrieve incoming request data
def get_incoming_data() -> dict:
    # Logic to retrieve and return incoming request data, typically using return request.get_json() in Flask applications
    pass

# Define a function to handle aborting the request
def handle_abort(message, code):
    # Logic to handle request abortion, in Flask applications it can be return abort(code, message)
    pass

# Define custom abort messages
custom_abort_messages = {
    'InvalidSignature': "Invalid signature.",
    'InvalidAccessToken': "Invalid access token.",
    # Add more custom abort messages as needed
}

# Define custom functions to run before Hetman authorization. For example, you could incorporate a function that verifies whether the IP Address is authorized.

custom_functions = [my_custom_function_1, my_custom_function_2]

# Configuration for the workspace
config = HetmanBaseConfig(
    incoming_data_getter=get_incoming_data,
    abort_function=handle_abort,
    abort_messages=custom_abort_messages, # Optional, use default messages instead
    own_functions_to_run=custom_functions # Optional
)
```

### Workspace Initialization

To work with Hetman, you need to initialize a workspace instance with your API key, API key secret, and workspace UUID. You can set a common configuration for all frames within the workspace or specify individual configurations for each frame.

```python
from hetman import HetmanWorkspace

# Common configuration for all frames within the workspace
workspace_config = HetmanBaseConfig(
    incoming_data_getter=get_incoming_data,
    abort_function=handle_abort,
    abort_messages=custom_abort_messages,
    own_functions_to_run=custom_functions
)

# Initialize workspace with common configuration
workspace = HetmanWorkspace(
    api_key="your_api_key",
    api_key_secret="your_api_key_secret",
    workspace_uuid="your_workspace_uuid",
    config=workspace_config
)
```

### Frame Initialization

You can initialize a frame within a workspace with its own configuration, inheriting from the workspace configuration or with a unique configuration.

```python
from hetman import HetmanFrame

# Inherit configuration from workspace
frame_1 = HetmanFrame(
    workspace=workspace,
    frame_uuid="frame_1_uuid",
    signature_secret="frame_1_signature_secret"
)

# Use unique configuration for the frame
frame_2_config = HetmanBaseConfig(
    incoming_data_getter=get_incoming_data_frame_2,
    abort_function=handle_abort_frame_2,
    abort_messages=custom_abort_messages_frame_2,
    own_functions_to_run=custom_functions_frame_2
)

frame_2 = HetmanFrame(
    workspace=workspace,
    frame_uuid="frame_2_uuid",
    signature_secret="frame_2_signature_secret",
    config=frame_2_config
)
```

### Authorization

Hetman provides authorization functionalities through decorators. You can use the `authorize_request` decorator to secure your endpoints.

```python
from hetman import HetmanAuth

@HetmanAuth.authorize_request(frame_1)
def my_secure_endpoint():
    # Your secure endpoint logic here
```

You can utilize the function (useful for debugging bugs). You have the option to employ the `authorize_func` function to protect your endpoints.

```python
from hetman import HetmanAuth

def my_secure_endpoint():
    HetmanAuth(
        frame, incoming_request_data # Pass here request data (For Flask request.get_json())
    ).authorize_func()

    # Your secure endpoint logic here
```

## Exceptions

Hetman raises several ***customizable*** exceptions to handle authorization errors:

- `MissingData`: Raised if required data is missing.
- `FrameUUIDDismatch`: Raised if the frame UUID mismatches.
- `InvalidAccessToken`: Raised if the access token is invalid.
- `InvalidSignature`: Raised if the signature is invalid.
- `NotFoundInAuthorizedMembers`: Raised if the workspace member is not found in authorized members.

## Contributing

Contributions to Hetman are welcome! If you encounter any issues or have suggestions for improvements, please submit them through the GitHub repository.
