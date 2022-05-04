from __future__ import unicode_literals

import django_eventstream as dje
from django.conf import settings
from django.http import HttpResponseBadRequest
from django_eventstream.eventrequest import EventRequest
from django_eventstream.eventstream import EventPermissionError, get_events
from django_eventstream.utils import add_default_headers, sse_error_response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from feedapp import models, views


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def handle_producer_event(request, **kwargs):
    """Handle events incoming from producers. Add authentication on top of the request."""
    # TODO: make sure long lived request works even with drf auth
    return handle_event(request, **kwargs)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def handle_consumer_event(request, **kwargs):
    """Handle events incoming from consumers.
    Validate query format, find an active producer channel, and if successful, forward event.

    """
    if (
        "task" not in request.data
        or request.data.get("task") not in settings.SUPPORTED_TASKS
        or "data" not in request.data
        or not request.data.get("data")
    ):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            # find active cluster + producer & their channel
            channel, cluster, producer = views.find_active_channel(request.user)
            if not channel:
                return Response(
                    {"detail": "no available resources"},
                    status=status.HTTP_418_IM_A_TEAPOT,
                )

            # create a query record with query id
            record = models.QueryRecord(
                task=request.data.get("task"),
                status="pending",
                consumer=request.user,
                producer=producer,
                cluster=cluster,
            )
            record.save()

            # send message to producer on event channel
            dje.send_event(
                channel,
                "message",
                {
                    "task": request.data.get("task"),
                    "data": request.data.get("data"),
                    "qid": record.id,
                },
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return handle_event(request, **kwargs)


def handle_event(request, **kwargs):
    """Standard event handler function, tweaked for drf."""
    print("hello from event handler")
    try:
        event_request = EventRequest(request, view_kwargs=kwargs)
        event_response = get_events(event_request)
        response = event_response.to_http_response(request)
    except EventRequest.ResumeNotAllowedError as e:
        response = HttpResponseBadRequest("Invalid request: %s.\n" % str(e))
    except EventRequest.GripError as e:
        if request.grip.proxied:
            response = sse_error_response("internal-error", "Invalid internal request.")
        else:
            response = sse_error_response(
                "bad-request", "Invalid request: %s." % str(e)
            )
    except EventRequest.Error as e:
        response = sse_error_response("bad-request", "Invalid request: %s." % str(e))
    except EventPermissionError as e:
        response = sse_error_response("forbidden", str(e), {"channels": e.channels})

    add_default_headers(response)

    return response
