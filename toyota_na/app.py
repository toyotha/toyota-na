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
    subparsers = parser.add_subparsers(title="command", dest="command", required=True)
    subparsers.add_parser("get_user_vehicle_list")
    subparsers.add_parser("get_vehicle_detail").add_argument("vin")
    subparsers.add_parser("get_vehicle_health_report").add_argument("vin")
    subparsers.add_parser("get_vehicle_health_status").add_argument("vin")
    subparsers.add_parser("get_vehicle_status").add_argument("vin")
    subparsers.add_parser("authorize").add_argument("code", nargs="?", default=None, help="Provide the code to fully login, otherwise to get the code.")
    args = parser.parse_args(sys.argv[1:])
    command = args.command
    command_kwargs = {k: v for k, v in vars(args).items() if k != "command"}
    
    cli = ToyotaOneClient(
        ToyotaOneAuth(callback=lambda tokens: save_tokens(tokens, AUTH_FILE))
    )

    if command == "authorize":
        if args.code:
            run_async(cli.auth.login(args.code))
            logging.info("Tokens saved")
        else:
            code = cli.auth.authorize()
            logging.info("Authorization code: %s", code)
        return

    try:
        with open(AUTH_FILE, "r") as f:
            saved_tokens = json.load(f)
            cli.auth.set_tokens(saved_tokens)
    except:
        pass

    if not cli.auth.logged_in():
        run_async(cli.auth.login())

    result = run_async(getattr(cli, command)(**command_kwargs))
    print(json.dumps(result, indent=2))


def save_tokens(tokens, auth_file):
    with open(auth_file, "w") as f:
        json.dump(tokens, f, indent=2)


def run_async(future):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(future)


if __name__ == "__main__":
    main()
