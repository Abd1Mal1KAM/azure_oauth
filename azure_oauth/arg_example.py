# utils/arg_example.py

"""_summary_"""

import argparse

parser = argparse.ArgumentParser(
    prog="Oauth2",
    description="""
        Authenticates the user after entering:
        - SERVICE
        - CLIENT_ID
        - CLIENT_SECRET
        - REDIRECT_URI
        - SCOPES
        """,
)

parser.add_argument(
    "--SERVICE",
    type=str,
    help="Service for app which requires authentication, e.g. Azure",
)
parser.add_argument(
    "--CLIENT_ID", type=str, help="Personal Client id for registered app"
)
parser.add_argument(
    "--CLIENT_SECRET", type=str, help="Personal Client Secret for registered app"
)
parser.add_argument(
    "--REDIRECT_URI",
    type=str,
    help="URL to redirect to during the authorization process",
)
parser.add_argument(
    "--SCOPES",
    default="",
    type=str,
    help="Scopes provided to the user depending on which apis need to be called",
)
