# toyota-na
Python client for Toyota North America service API

# Install
```
pip install toyota-na[qt]
```
[qt] is required for generating authorization code.
# Usage
```
python -m toyota_na.app -h  # Get help
python -m toyota_na.app get_user_vehicle_list  # List vehicle
python -m toyota_na.app get_vehicle_status <vin>  # Get vehcicle status
...
```

# Developer Guide
## Quick Start
```
from toyota_na.client import ToyotaOneClient
cli = ToyotaOneClient()
cli.auth.login()
vehicle_list = cli.get_user_vehicle_list()
vehicle_status = cli.get_vehicle_status(vehicle_list[0]["vin])
...
```
## About authorization
Toyota OAuth2 service require the redirect_uri to be "com.toyota.oneapp:/oauth2Callback".
we need to mock this app. We use PyQt5 to intercept the redirection in this module.
Qt5 application can not be launched in a server side setup, such as Home Assistant.
Alternatively, the login can be separated to two steps here:
1. Get the authorization code (requires Qt5)
2. Use the code to retrieve the tokens


To get the authorization code:
```
python -m toyota_na.app authorize
```
To use the authorization code:
- In python code:
```
from toyota_na.client import ToyotaOneClient
cli = ToyotaOneClient()
cli.auth.login(authorization_code)
```
- In CLI:
```
python -m toyota_na.app authorize <authorization_code>
```
## Samples
Sample responses from API calls are stored in `samples` folder. The data is from Toyota app's "Demo Mode"