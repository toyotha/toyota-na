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

### Abstracted Interface Example
```
from toyota_na.client import ToyotaOneClient
from toyota_na.vehicle.vehicle import get_vehicles

async def main():
    cli = ToyotaOneClient()
```

### Contributing
We use black and isort for opinionated formatting to ensure a consistent look and feel throughout the codebase no matter the contributor.
Pre-commit is used to guarantee the files being check in to the repo are formatted correctly.

For convenience a vscode project settings file is included as well. Editors other than vscode will require some setup if you wish to have formatting take place while working.

Getting started:
- Clone the repo
- `pip3 install black isort pre-commit`
- `pre-commit install`

### Samples
Sample responses from API calls are stored in `samples` folder. The data is from Toyota app's "Demo Mode"

## Credits:
Thanks @DurgNomis-drol for making the original Toyota module and bring up the discussing of Toyota North America.

Thanks @visualage for finding the way to authenticate headlessly.
