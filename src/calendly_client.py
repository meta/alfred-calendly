#!/usr/bin/python
# encoding: utf-8

import constants as c
from workflow import Workflow3, web

log = Workflow3().logger


class CalendlyClient:

    client_id = ""
    client_secret = ""
    redirect_uri = ""

    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def authorize(self, code):
        response = web.post(
            url="%s%s" % (c.CALENDLY_AUTH_BASE_URL, c.CALENDLY_TOKEN_URI),
            data={
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "redirect_uri": self.redirect_uri
            }
        )
        response.raise_for_status()

        if response.status_code == 200:
            return {
                c.ACCESS_TOKEN: response.json()["access_token"],
                c.REFRESH_TOKEN: response.json()["refresh_token"]
            }
        else:
            log.error("Authorization request failed. Calendly returned status [%s]. Response payload below." % response.status_code)
            log.error(response.json())
            return None

    """Introspects the Token. Returns True only when request succeeded and token is still active"""
    def introspect(self, access_token):
        response = web.post(
            url="%s%s" % (c.CALENDLY_AUTH_BASE_URL, c.CALENDLY_INTROSPECT_URI),
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "token": access_token
            }
        )
        response.raise_for_status()

        if response.status_code == 200:
            return response.json()["active"]
        else:
            log.error("Introspecting access token failed. Calendly returned status [%s]. Response payload below." % response.status_code)
            log.error(response.json())
            return False

    def refresh_token(self, refresh_token):
        response = web.post(
            url="%s%s" % (c.CALENDLY_AUTH_BASE_URL, c.CALENDLY_TOKEN_URI),
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            }
        )
        response.raise_for_status()

        if response.status_code == 200:
            log.debug("Access Token refreshed.")
            response_json = response.json()
            return {
                c.ACCESS_TOKEN: response_json["access_token"],
                c.REFRESH_TOKEN: response_json["refresh_token"]
            }
        else:
            log.error("Refreshing the access token failed. Calendly returned status [%s]. Response payload below." % response.status_code)
            log.error(response.json())
            return None

    def create_scheduling_link(self):
        pass

    def get_event_types_of_user(self, user, access_token):
        log.debug("in: get_event_types_of_user")
        response = web.get(
            url="%s%s" % (c.CALENDLY_API_BASE_URL, c.CALENDLY_EVENT_TYPES_URI),
            headers={
                "Authorization": "Bearer %s" % access_token,
            },
            params={
                "user": user
            }
        )
        response.raise_for_status()

        if response.status_code == 200:
            return response.json()["collection"]
        else:
            log.error("Getting Event Types failed. Calendly returned status [%s]. Response payload below." % response.status_code)
            log.error(response.json())
            return None

    def get_current_user(self, access_token):
        log.debug("in: get_current_user")
        response = web.get(
            url="%s%s" % (c.CALENDLY_API_BASE_URL, c.CALENDLY_CURRENT_USER_URI),
            headers={
                "Authorization": "Bearer %s" % access_token,
            }
        )
        response.raise_for_status()

        if response.status_code == 200:
            return response.json()["resource"]["uri"]
        else:
            log.error("Getting current user failed. Calendly returned status [%s]. Response payload below." % response.status_code)
            log.error(response.json())
            return None

    def create_link(self, event_type, event_count, access_token):
        log.debug("in: create_link")
        log.debug("Event Type: [%s], Max. Event Count: [%d]" % (event_type, event_count))

        response = web.post(
            url="%s%s" % (c.CALENDLY_API_BASE_URL, c.CALENDLY_SCHEDULING_LINK_URI),
            headers={
                "Authorization": "Bearer %s" % access_token,
            },
            data={
                "max_event_count": event_count,
                "owner": event_type,
                "owner_type": "EventType"
            }
        )
        response.raise_for_status()

        if response.status_code == 201:
            return response.json()["resource"]["booking_url"]
        else:
            log.error(
                "Creating a link failed. Calendly returned status [%s]. Response payload below." % response.status_code)
            log.error(response.json())
            return None
