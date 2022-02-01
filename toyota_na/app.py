import argparse
import asyncio
import json
import logging
import sys

from .auth import ToyotaOneAuth
from .client import ToyotaOneClient


def configure_logger():
    logging.basicConfig(
        stream=sys.stdout,
        format="%(levelname)s %(asctime)s - %(message)s",
        level=logging.INFO,
    )


def main():
    configure_logger()
    AUTH_FILE = ".toyota_na_tokens.json"
    DEVICE_ID_FILE = ".toyota_na_device_id"
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        title="command", dest="sub_command", required=True
    )
    subparsers.add_parser("get_user_vehicle_list")
    subparsers.add_parser("get_vehicle_detail").add_argument("vin")
    subparsers.add_parser("get_vehicle_health_report").add_argument("vin")
    subparsers.add_parser("get_vehicle_health_status").add_argument("vin")
    subparser = subparsers.add_parser("get_vehicle_status")
    subparser.add_argument("vin")
    subparser.add_argument(
        "generation", choices=["17CYPLUS", "17CY"], nargs="?", default="17CYPLUS"
    )
    subparser = subparsers.add_parser("get_engine_status")
    subparser.add_argument("vin")
    subparser.add_argument(
        "generation", choices=["17CYPLUS", "17CY"], nargs="?", default="17CYPLUS"
    )
    subparser = subparsers.add_parser("get_telemetry")
    subparser.add_argument("vin")
    subparser.add_argument(
        "generation", choices=["17CYPLUS", "17CY"], nargs="?", default="17CYPLUS"
    )
    subparser = subparsers.add_parser("send_refresh_status")
    subparser.add_argument("vin")
    subparser.add_argument(
        "generation", choices=["17CYPLUS", "17CY"], nargs="?", default="17CYPLUS"
    )
    sub_parser = subparsers.add_parser("remote_request")
    sub_parser.add_argument("vin")
    sub_parser.add_argument(
        "command",
        choices=[
            "door-lock",
            "door-unlock",
            "engine-start",
            "engine-stop",
            "hazard-on",
            "hazard-off",
            "power-window-on",
            "power-window-off",
            "ac-settings-on",
            "sound-horn",
            "buzzer-warning",
            "find-vehicle",
            "ventilation-on",
            "DL",
            "RES",
            "HZ",
        ],
    )
    sub_parser.add_argument("value", choices=[1, 2], type=int, nargs="?", default=None)
    sub_parser.add_argument(
        "generation", choices=["17CYPLUS", "17CY"], nargs="?", default="17CYPLUS"
    )
    sub_parser = subparsers.add_parser("authorize")
    sub_parser.add_argument("username")
    sub_parser.add_argument("password")
    args = parser.parse_args(sys.argv[1:])
    sub_command = args.sub_command
    sub_command_kwargs = {k: v for k, v in vars(args).items() if k != "sub_command"}

    cli = ToyotaOneClient(
        ToyotaOneAuth(callback=lambda tokens: save_tokens(tokens, AUTH_FILE))
    )

    if sub_command == "authorize":
        run_async(cli.auth.login(args.username, args.password))
        return

    try:
        with open(AUTH_FILE, "r") as f:
            saved_tokens = json.load(f)
            cli.auth.set_tokens(saved_tokens)
    except:
        logging.error("Not logged in")
        return
    try:
        with open(DEVICE_ID_FILE, "r") as f:
            saved_device_id = f.read()
            cli.auth.set_device_id(saved_device_id)
    except:
        device_id = cli.auth.get_device_id()
        try:
            save_device_id(device_id, DEVICE_ID_FILE)
        except Exception as err:
            logging.error("Unable to save device id: %s", err)
        logging.warning("No device ID loaded; new ID generated: %s", device_id)

    result = run_async(getattr(cli, sub_command)(**sub_command_kwargs))
    print(json.dumps(result, indent=2))


def save_tokens(tokens, auth_file):
    with open(auth_file, "w") as f:
        json.dump(tokens, f, indent=2)


def save_device_id(device_id, device_id_file):
    with open(device_id_file, "w") as f:
        f.write(device_id)


def run_async(future):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(future)


if __name__ == "__main__":
    main()
