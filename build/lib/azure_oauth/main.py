# main.py
"""
This script handles OAuth2 authentication for a specified service.
The script performs the following tasks:
1. Checks the Python version.
2. Creates a virtual environment.
3. Installs necessary dependencies.
4. Parses command-line arguments for OAuth2 credentials.
5. Prompts the user for any missing credentials.
6. Authenticates the user using OAuth2.
Functions:
    initialise: Sets up the environment by:
    Checking the Python version, 
    Creating a virtual environment, 
    Installing dependencies.
    main: The main entry point of the script. 
    Parses command-line arguments, prompts for missing credentials, and authenticates the user.
Usage:
    python main.py 
    --SERVICE <service> 
    --CLIENT_ID <client_id> 
    --CLIENT_SECRET <client_secret> 
    --REDIRECT_URI <redirect_uri> 
    --SCOPES <scopes>
    Initializes the environment by performing the following tasks:
    - Checks if the correct version of Python is being used.
    - Creates a virtual environment in the current directory.
    - Installs necessary dependencies in the virtual environment.
    pass
    The main entry point of the script. It performs the following tasks:
    - Initializes the environment.
    - Parses command-line arguments for OAuth2 credentials.
    - Prompts the user for any missing credentials.
    - Authenticates the user using OAuth2.
    Command-line Arguments:
        --SERVICE: The service for the app which requires authentication (e.g., Azure).
        --CLIENT_ID: The personal client ID for the registered app.
        --CLIENT_SECRET: The personal client secret for the registered app.
        --REDIRECT_URI: The redirect URI for the OAuth2 authentication.
        --SCOPES: The scopes for the OAuth2 authentication (default is an empty string).
    pass
"""

import os
from argparse import Namespace
from oauth_handler import OAuth2
from arg_example import parser

from utils.general import check_python, install_dependencies, create_venv, exit_code #type: ignore

def initialise() -> None:
    """_summary_"""
    check_python()

    current_dir = os.getcwd()
    create_venv(current_dir)
    install_dependencies(current_dir)

@exit_code
def main() -> None:
    """Main Entry Point"""

    initialise()

    args: Namespace = parser.parse_args()

    service: str = (args.SERVICE).lower()

    client_id: str = args.CLIENT_ID
    client_secret: str = args.CLIENT_SECRET

    redirect_uri: str = args.REDIRECT_URI

    scopes: str = args.SCOPES

    app = OAuth2(service, redirect_uri, client_id, client_secret, scopes)

    print("Press Ctrl + C to exit")

    app.authenticate()


if __name__ == "__main__":
    main()
