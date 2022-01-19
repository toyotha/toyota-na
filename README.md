# toyota-na
Python client for Toyota North America service API

## Install
```
pip install toyota-na
```
## Usage
```
python -m toyota_na.app -h  # Get help
python -m toyota_na.app authorize <username> <passworde>
python -m toyota_na.app get_user_vehicle_list  # List vehicle
python -m toyota_na.app get_vehicle_status <vin>  # Get vehcicle status
...
```

## Known Issues
1. Not working for older models. Currently it only works on generation "17CYPLUS" as identified in the result of `get_user_vehicle_list`
2. Door/window status not always up-to-date unless you call `send_refresh_status` first and wait for it to complete (there is no notification that it completed successfully).

## Developer Guide
### Quick Start
```
from toyota_na.client import ToyotaOneClient

async def main():
    cli = ToyotaOneClient()
    await cli.auth.login(USERNAME, PASSWORD)
    vehicle_list = await cli.get_user_vehicle_list()
    vehicle_status = await cli.get_vehicle_status(vehicle_list[0]["vin])
    ...
```
### Samples
Sample responses from API calls are stored in `samples` folder. The data is from Toyota app's "Demo Mode"

## Credits:
Thanks @DurgNomis-drol for making the original Toyota module and bring up the discussing of Toyota North America.

Thanks @visualage for finding the way to authenticate headlessly.
