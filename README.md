# toyota-na
Python client for Toyota North America service API

# Usage (CLI)
```
python -m toyota_na.app -h  # Get help
python -m toyota_na.app get_user_vehicle_list  # List vehicle
python -m toyota_na.app get_vehicle_status <vin>  # Get vehcicle status
...
```

# Usage 
```
from toyota_na.client import ToyotaOneClient
cli = ToyotaOneClient()
cli.auth.login()
vehicle_list = cli.get_user_vehicle_list()
vehicle_status = cli.get_vehicle_status(vehicle_list[0]["vin])
...
```
