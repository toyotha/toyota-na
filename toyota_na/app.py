import sys
import json
import logging
import argparse

from .client import ToyotaOneClient


def configure_logger():
    logging.basicConfig(
        stream=sys.stdout,
        format="%(levelname)s %(asctime)s - %(message)s",
        level=logging.INFO
    )


def main():
    configure_logger()

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
    
    cli = ToyotaOneClient()

    if command == "authorize":
        if args.code:
            cli.auth.login(args.code)
            logging.info("Tokens saved")
        else:
            code = cli.auth.authorize()
            logging.info("Authorization code: %s", code)
        return

    if not cli.auth.logged_in():
        cli.auth.login()

    result = getattr(cli, command)(**command_kwargs)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
