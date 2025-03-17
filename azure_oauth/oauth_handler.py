# oauth_handler.py

"""_summary_"""

import time
import sys
import webbrowser
from typing import Tuple, Optional, Dict
import json
from pathlib import Path

from flask import request as req, Flask, redirect

from helpers import (
    create_random_string,
    get_many,
    handle_response,
)

with open(Path(__file__).parent / "service_config.json", encoding="utf-8") as file:
    service_config: Dict[str, Dict[str, str]] = json.load(file)


class OAuth2:
    """_summary_"""

    RESPONSE_TYPE = "Assertion"
    STATE = create_random_string()

    app = Flask(__name__)

    def __init__(
        self,
        service: Optional[str],
        redirect_uri: Optional[str],
        client_id: Optional[str],
        client_secret: Optional[str],
        scopes: Optional[str],
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

        service_info = self.get_service_info(service)
        self.authorization_url = service_info[0]
        self.token_url = service_info[1]
        self.base_url = service_info[2]
        self.scopes = scopes

    def get_service_info(
        self, chosen_service: Optional[str]
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """_summary_

        Returns:
            Tuple[Optional[str], Optional[str]]: _description_
        """

        if not chosen_service:
            print(
                f"\nService provided: {chosen_service} is null.\n"
                + "\nPress Ctrl + C to start again"
            )
            return (None, None, None)

        org_data = service_config.get(chosen_service)
        if not isinstance(org_data, dict):
            org_data = None

        if org_data is not None:
            base_url = org_data.get("BASE_URL")
            auth_url = org_data.get("AUTH_URL")
            token_url = org_data.get("TOKEN_URL")
        else:
            print(f"\nService provided: {chosen_service} does not have stored urls.")
            return (None, None, None)

        return (auth_url, token_url, base_url)

    @app.route("/auth")
    def authorize(self):
        """_summary_

        Returns:
            _type_: _description_
        """

        if not self.authorization_url:
            return None

        authorization_url = (
            f"{self.authorization_url}"
            + f"?client_id={self.client_id}&response_type={self.RESPONSE_TYPE}&state={self.STATE}"
            + f"&scope={self.scopes}&redirect_uri={self.redirect_uri}"
        )

        webbrowser.open(authorization_url)
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            sys.exit(1)

        return redirect(authorization_url)

    @app.route("/callback")
    def _get_access_token(
        self,
        refresh: bool = False,
        refresh_token: Optional[str] = None,
    ):
        """_summary_

        Args:
            refresh (bool, optional): _description_. Defaults to False.
            refresh_token (Optional[str], optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """

        if refresh and not refresh_token:
            print("\nRefresh_token is required when Refresh is True.\n")
            return None

        try:
            auth_code = req.args.get("code")
            state = req.args.get("state")
        except (RuntimeError, KeyError, TypeError):
            print("You either waited too long or your details are incorrect.")
            return None

        if state != self.STATE:
            print("\nAuthorization failed.\n")
            return None

        tokenize = handle_response(
            target_url=self.token_url if self.token_url else "",
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            body={
                "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                "client_assertion": self.client_secret,
                "grant_type": (
                    "refresh_token"
                    if refresh
                    else "urn:ietf:params:oauth:grant-type:jwt-bearer"
                ),
                "assertion": refresh_token if refresh else auth_code,
                "redirect_uri": self.redirect_uri,
            },
        )

        return tokenize

    def authenticate(
        self, refresh: bool = False, refresh_token: Optional[str] = None
    ) -> Optional[str]:
        """_summary_

        Args:
            refresh (bool, optional): _description_. Defaults to False.
            refresh_token (Optional[str], optional): _description_. Defaults to None.
        """

        if refresh and not refresh_token:
            print("\nRefresh_token is required when Refresh is True.\n")

        authorizer = self.authorize()

        if not authorizer:
            return None

        if not refresh:
            result = self._get_access_token()
        else:
            result = self._get_access_token(True, refresh_token)

        if result is None:
            return None

        access_token = get_many(result, ["access_token"])
        new_refresh_token = get_many(result, ["refresh_token"])
        expiry_time = get_many(result, ["expires_in"])

        print(
            f"\nAccess Token: {access_token}\n"
            + f"Expiry Time (s): {expiry_time}\n"
            + f"Refresh Token: {new_refresh_token}"
        )

        return access_token
