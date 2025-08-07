import argparse
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host",
        default="localhost",
        help="host for server to listen on, defaults to localhost"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="port for server to be hosted on, defaults to 8000"
    )
    parser.add_argument(
        "--development",
        action = "store_true",
        help = "development that is false until interacted with"
    )
    return parser.parse_args()