# helpers.py

"""_summary_"""
import os
import venv
import sys
import subprocess
import time
import random
import string
import re
import json

from functools import wraps
from typing import Optional, List, Union, TypeAlias, Dict, Callable, Any, get_args

import requests
import requests_cache

from requests import Response
from tenacity import retry, wait_fixed, stop_after_attempt

TIMEOUT = 10  # Duration to receive response before giving an error
WAIT_TIME = 3  # Time to wait between retries

requests_cache.install_cache()

AnyType: TypeAlias = Optional[Union[float, str, bool, List[Any], Any]]
Key: TypeAlias = Union[str, int, float]
IterableType: TypeAlias = Optional[Dict[AnyType, AnyType]]
JsonResponse: TypeAlias = Optional[Dict[Key, Key]]


def subcheck(commands: List[str], err_msg: Optional[str] = None) -> None:
    """Run a subprocess command and handle errors.

    Args:
        commands (List[str]): The list of command arguments to run.
        err_msg (Optional[str], optional):
            The error message to raise if the command fails. Defaults to None.

    Raises:
        RuntimeError: If the command fails and an error message is provided.
    """
    try:
        subprocess.check_call(commands)
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        subprocess.SubprocessError,
    ) as exc:
        if not err_msg:
            err_msg = "Failed to run task"

        raise RuntimeError(err_msg) from exc


def create_venv(venv_path: str) -> None:
    """Create a virtual environment in the given path.

    Args:
        venv_path (str): _description_
    """

    if not os.path.exists(venv_path):
        venv.create(venv_path, with_pip=True)
        print("Virtual Environment has been created")
    else:
        pass


def check_python() -> None:
    """Check if Python is installed and accessible."""

    subcheck(
        [sys.executable, "--version"],
        "Error: Python is not installed or not found in the system path."
        + "Please install Python from https://www.python.org/downloads/",
    )


def exit_code(func):
    """Decorator to handle KeyboardInterrupt and exit gracefully.

    This decorator wraps a function to catch the KeyboardInterrupt exception
    and exit the program gracefully when the exception is raised.

    Args:
        func (Callable): The function to decorate.

    Returns:
        Callable[[Any], Any]: The wrapped function.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print("\nExiting...")
            time.sleep(3)
            os.system("cls")
            sys.exit(0)

    return wrapper


def create_random_string() -> str:
    """Creates a random string.

    Returns:
        str: The generated random string.
    """
    random_str = "".join(random.choices(string.ascii_letters + string.digits, k=32))

    return random_str


def install_dependencies() -> None:
    """_summary_

    Args:
        folder_path (str): _description_
    """

    folder_path = os.getcwd()
    requirements_path = os.path.join(folder_path, "requirements.txt")

    if not os.path.exists(requirements_path):
        subcheck(["pip", "install", "--quiet", "pipreqs"], "Failed to install pipreqs")
        subcheck(
            ["pipreqs", folder_path, "--force"], "Failed to generate requirements file."
        )

    subcheck(
        [sys.executable, "-m", "pip", "install", "--quiet", "-r", requirements_path],
        "Failed to install dependencies from 'requirements.txt'",
    )


def get_many(
    iterable: IterableType,
    item_list: Union[List[Key], Key],
    default: Optional[Any] = None,
) -> Optional[Any]:
    """Retrieves multiple values from a dictionary.

    Args:
        iterable (IterableType): The dictionary to retrieve values from.
        item_list (Union[List[Key], Key]): The list of keys or a single key to retrieve.
        default (Optional[Any], optional):
            The default value if the key is not found. Defaults to None.

    Returns:
        Optional[Any]: The retrieved value or the default value.
    """

    if iterable is None:
        return default

    try:
        current = iterable.get(
            (item_list[0] if isinstance(item_list, get_args(List[Key])) else item_list),
            default,
        )
    except (AttributeError, IndexError):
        return default

    if isinstance(current, dict) and isinstance(item_list, get_args(List[Key])):
        return get_many(current, item_list[1:], default)

    return current


def extract_api_name(api_url: str) -> str:
    """Extracts the name of the api from its url

    Args:
        api_url (str): The api url

    Returns:
        str: The api name
    """
    domain_name, url_name = "", ""

    domain_pattern = r"https?://(?:[a-zA-Z0-9-]+\.)?([a-zA-Z0-9-]+)\.com/[^?]+"
    url_pattern = r"https?://(?:[a-zA-Z0-9-]+\.)?[a-zA-Z0-9-]+\.com/([^?]+)"

    domain_matches = re.search(domain_pattern, api_url)
    if domain_matches:
        try:
            domain_name = domain_matches.group(1)
        except IndexError:
            pass

    url_matches = re.search(url_pattern, api_url)
    if url_matches:
        try:
            url_name_list = url_matches.group(1).split("/")[:-1]
            url_name = " ".join(url_name_list)
        except IndexError:
            pass

    return f"{domain_name} {url_name}"


@retry(
    stop=stop_after_attempt(WAIT_TIME),
    wait=wait_fixed(WAIT_TIME),
)
def handle_response(
    target_url: str,
    method: str = "GET",
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
    body: Optional[dict] = None,
    column: Optional[str] = None,
    display_error_messages: Optional[bool] = False,
) -> Union[JsonResponse, Key]:
    """Handles the API response with retry logic and error handling.

    Args:
        target_url (str): The target URL for the API request.
        method (str, optional): The HTTP method to use for the request. Defaults to "GET".
        params (Optional[dict], optional):
            The query parameters to include in the request. Defaults to None.
        headers (Optional[dict], optional): The headers to include in the request. Defaults to None.
        body (Optional[dict], optional): The body data to include in the request. Defaults to None.
        column (Optional[str], optional):
            The specific column to extract from the response JSON. Defaults to None.
        display_error_messages (Optional[bool], optional):
            Whether to display error messages. Defaults to False.

    Returns:
        Union[JsonResponse, Key]: The JSON response or a specific key from the response.
    """

    response_func: Callable = getattr(requests, method.lower())

    try:
        response: Response = response_func(
            url=target_url, timeout=TIMEOUT, headers=headers, json=body, params=params
        )
        response.raise_for_status()
        if not response.ok:
            api_name: str = extract_api_name(target_url)
            try:
                response_text: dict = response.json()
                response_error_text = get_many(
                    response_text, ["error", "message"], response_text
                )
            except (TypeError, json.decoder.JSONDecodeError):
                response_error_text = response.text

            if display_error_messages:
                print(
                    f"\nError in API: {api_name}\n"
                    f"Status: {response.status_code}\n"
                    f"Response: {response_error_text}\n"
                    f"Method: {method.upper()} URL: {target_url}"
                )
            return None

        data: dict = response.json()
    except requests.exceptions.Timeout:
        print(f"\nThe response: \n{target_url}timed out after {TIMEOUT} seconds")
        return None
    except requests.exceptions.HTTPError as http_err:
        print(f"\nThe response raised a HTTP Error: \n{http_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"\nRequest Error: {req_err}")
        return None

    result = data.get(column, None) if column else data

    if result is None:
        print(f"\nResult does not exist when searching for: \n{target_url}\n")
        return None

    return result
