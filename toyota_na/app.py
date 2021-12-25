import sys
import json
import logging
import argparse
import asyncio

from .client import ToyotaOneClient
from .auth import ToyotaOneAuth


def configure_logger():
    logging.basicConfig(
        stream=sys.stdout,
        format="%(levelname)s %(asctime)s - %(message)s",
        level=logging.INFO
    )


def main():
    configure_logger()
    AUTH_FILE = ".toyota_na_tokens.json"
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="command", dest="sub_command", required=True)
    subparsers.add_parser("get_user_vehicle_list")
    subparsers.add_parser("get_vehicle_detail").add_argument("vin")
    subparsers.add_parser("get_vehicle_health_report").add_argument("vin")
    subparsers.add_parser("get_vehicle_health_status").add_argument("vin")
    subparsers.add_parser("get_vehicle_status").add_argument("vin")
    subparsers.add_parser("get_odometer_detail").add_argument("vin")
    subparsers.add_parser("send_refresh_status").add_argument("vin")
    sub_parser = subparsers.add_parser("remote_request")
    sub_parser.add_argument("vin")
    sub_parser.add_argument("command", choices=[
        "door-lock", "door-unlock", "engine-start", "engine-stop",
        "hazard-on", "hazard-off", "power-window-on", "power-window-off",
        "ac-settings-on", "sound-horn", "buzzer-warning",
        "find-vehicle", "ventilation-on"])
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

    result = run_async(getattr(cli, sub_command)(**sub_command_kwargs))
    print(json.dumps(result, indent=2))


def save_tokens(tokens, auth_file):
    with open(auth_file, "w") as f:
        json.dump(tokens, f, indent=2)


def run_async(future):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(future)


if __name__ == "__main__":
    main()
