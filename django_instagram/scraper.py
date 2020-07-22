"""
Created on 04/sep/2016

@author: Marco Pompili
"""

from socket import error as socket_error
from lxml import html
import requests
from requests.exceptions import ConnectionError, HTTPError
import json
import logging

SCRIPT_JSON_PREFIX = 18
SCRIPT_JSON_DATA_INDEX = 21

# Adding headers because instagram is sending requests to login without a session.
HTTP_HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
    'accept': '*/*',
    'accept-language': 'es-US,es-419;q=0.9,es;q=0.8,en;q=0.7',
}


def instagram_scrap_profile(username):
    """
    Scrap an instagram profile page
    :param username:
    :return:
    """
    try:
        url = "https://www.instagram.com/{}/".format(username)
        page = requests.get(url, headers=HTTP_HEADERS)
        # Raise error for 404 cause by a bad profile name
        page.raise_for_status()
        return html.fromstring(page.content)
    except HTTPError:
        logging.exception('user profile "{}" not found'.format(username))
    except (ConnectionError, socket_error) as e:
        logging.exception("instagram.com unreachable")


def instagram_profile_js(username):
    """
    Retrieve the script tags from the parsed page.
    :param username:
    :return:
    """
    try:
        tree = instagram_scrap_profile(username)
        return tree.xpath('//script')
    except AttributeError:
        logging.exception("scripts not found")
        return None


def instagram_profile_json(username):
    """
    Get the JSON data string from the scripts.
    :param username:
    :return:
    """
    scripts = instagram_profile_js(username)
    source = None

    if scripts:
        for script in scripts:
            if script.text:
                if script.text[0:SCRIPT_JSON_PREFIX] == "window._sharedData":
                    source = script.text[SCRIPT_JSON_DATA_INDEX:-1]

    return source


def instagram_profile_obj(username):
    """
    Retrieve the JSON from the page and parse it to a python dict.
    :param username:
    :return:
    """
    json_data = instagram_profile_json(username)
    return json.loads(json_data) if json_data else None
