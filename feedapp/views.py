import functools
from datetime import datetime
from urllib.parse import quote_plus, urlencode

import django_eventstream as dje
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Cluster, QueryRecord, User

# current way to store query results and statuses
QUERY_STORE = {}


oauth = OAuth()

oauth.register(
    "auth0",
    client_id=settings.SOCIAL_AUTH_AUTH0_KEY,
    client_secret=settings.SOCIAL_AUTH_AUTH0_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.SOCIAL_AUTH_AUTH0_DOMAIN}/.well-known/openid-configuration",
)


def index(request):
    print("following up and getting here", request.user, request.session.get("user"))
    if request.user and not isinstance(request.user, AnonymousUser):
        token, created = Token.objects.get_or_create(user=request.user)
        return redirect(
            f"{settings.HULSE_DASHBOARD_URL}?"
            + urlencode(
                {
                    "authToken": token.key,
                    "email": request.user.email,
                    "username": request.user.username,
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name,
                    "picture": None
                    if not request.session
                    or not request.session.get("user")
                    or not request.session.get("user").get("userinfo")
                    else request.session.get("user").get("userinfo").get("picture"),
                },
                quote_via=quote_plus,
            ),
        )

    return redirect(settings.HULSE_LANDING_URL)


def callback(request):
    # if already registered the user and returning from alternative auth0 login
    print("reached a callback\n\n")
    if request.session.get("user") and not isinstance(request.user, AnonymousUser):
        print(request.user, request.session.get("user"))
        return redirect(request.build_absolute_uri(reverse("index")))

    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token
    return redirect(request.build_absolute_uri("/login/auth0"))


def login(request):
    """Login through Auth0."""
    print(
        "CALLBACK LOGIN",
        request.build_absolute_uri(
            reverse("callback")
        ),  # .replace("https://", "https://"),
    )
    return oauth.auth0.authorize_redirect(
        request,
        request.build_absolute_uri(
            reverse("callback")
        ),  # .replace("https://", "https://"),
    )


def logout(request):
    request.session.clear()

    return redirect(
        f"https://{settings.SOCIAL_AUTH_AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("index")),
                "client_id": settings.SOCIAL_AUTH_AUTH0_KEY,
            },
            quote_via=quote_plus,
        ),
    )


def serialize_clusters(clusters, user):
    """Dump user clusters to a dict and return response.

    :param clusters: Clusters of requesting users.
    :type clusters: List
    :param user: User to serialize clusters for.
    :type user: django.auth.models.User
    :return: HTTP response with attached json dumped clusters.
    :rtype: rest_framework.response.Response
    """
    serialized_clusters = []
    for cluster in clusters:
        # skip clusters that were deleted
        if cluster.deleted:
            continue

        serialized_clusters.append(
            {
                "id": cluster.id,
                "name": cluster.name,
                "description": cluster.description,
                "created_at": cluster.date_created.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": cluster.date_updated.strftime("%Y-%m-%d %H:%M:%S"),
                "member_count": cluster.members.count(),
                "is_admin": (cluster.admin == user),
            }
        )
    return Response(data={"clusters": serialized_clusters}, status=status.HTTP_200_OK)


def get_user_clusters(uid):
    user = User.objects.filter(id=uid).first()
    return serialize_clusters(user.clusters.all(), user)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_cluster(request):
    if "name" not in request.data or "description" not in request.data:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    new_cluster = Cluster(
        name=request.data["name"],
        description=request.data["description"],
        admin=request.user,
    )
    new_cluster.save()
    new_cluster.members.add(request.user)
    new_cluster.save()

    return get_user_clusters(request.user.id)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_cluster(request):
    if "cluster_id" not in request.data:
        return Response(
            data={"error": "cluster id missing from request"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cluster = Cluster.objects.filter(id=request.data["cluster_id"]).first()
    if request.user != cluster.admin:
        return Response(
            data={"error": "user does not have the right to delete cluster"},
            status=status.HTTP_403_FORBIDDEN,
        )

    cluster.deleted = True
    cluster.deleted_by = request.user
    cluster.date_deleted = datetime.now()
    cluster.save()

    return Response(data={"deleted": True}, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def edit_cluster(request):
    if (
        "name" not in request.data
        or "description" not in request.data
        or "cluster_id" not in request.data
    ):
        return Response(
            data={"error": "incomplete request"}, status=status.HTTP_400_BAD_REQUEST
        )

    cluster = Cluster.objects.filter(id=request.data["cluster_id"]).first()
    if request.user != cluster.admin:
        return Response(
            data={"error": "user does not have the rights to edit cluster"},
            status=status.HTTP_403_FORBIDDEN,
        )

    cluster.name = request.data["name"]
    cluster.description = request.data["description"]
    cluster.save()

    return Response(data={"edited": True}, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def leave_cluster(request):
    if "cluster_id" not in request.data:
        return Response(
            data={"error": "cluster id missing from request"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cluster = Cluster.objects.filter(id=request.data["cluster_id"]).first()
    # make sure not already part of this cluster
    if cluster.deleted or request.user not in cluster.members.all():
        return Response(
            data={"error": "cluster was deleted or user not a part of it"},
            status=status.HTTP_403_FORBIDDEN,
        )

    cluster.members.remove(request.user)
    cluster.save()

    return Response(data={"left": True}, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def join_cluster(request):
    if "cluster_id" not in request.data:
        return Response(
            data={"error": "cluster id missing from request"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cluster = Cluster.objects.filter(id=request.data["cluster_id"]).first()
    # make sure not already part of this cluster
    if cluster.deleted or request.user in cluster.members.all():
        return Response(
            data={"error": "cluster was deleted or user already part of it"},
            status=status.HTTP_403_FORBIDDEN,
        )

    cluster.members.add(request.user)
    cluster.save()

    return Response(data={"joined": True}, status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_clusters(request):
    return get_user_clusters(request.user.id)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def query(request):
    """Entrypoint for model queries from python client & authenticated users.
    Here forward query to a connected team host or return an error if none are available.
    Check requests has input data and fits the available tasks.
    """
    # TODO: switch to using drf serializers
    # validate format of the data
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
            channel, cluster, producer = find_active_channel(request.user)
            if not channel:
                return Response({}, status=status.HTTP_418_IM_A_TEAPOT)

            # create a query record with query id
            record = QueryRecord(
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
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        # post awaiting response for qid in key value store
        return Response({"qid": record.id}, status=status.HTTP_200_OK)


def find_active_channel(user):
    """Lookup event streams for active producer channels, and find a cluster with
    a producer to which requesting user has access.

    :param user: User posting a query.
    :type user: django.contrib.auth.models.User
    :return: Producer channel name.
    :rtype: str
    """
    # find all events that match the current request
    # find all people
    user_candidate_channels = {}
    for cluster in user.clusters.all():
        for member in cluster.members.all():
            token, created = Token.objects.get_or_create(user=member)
            user_candidate_channels[f"producer-{token.key}"] = (cluster, member)

    if len(user_candidate_channels) == 0:
        return None, None, None

    # print("candidate channels", user_candidate_channels)

    # retrieve all active channels
    condition = functools.reduce(
        lambda q, f: q | Q(channel__startswith=f),
        list(user_candidate_channels),
        Q(),
    )

    # TODO: figure out how to activate storage
    all_channels = dje.models.Event.objects.all()

    active_channels = set(
        [event.channel for event in dje.models.Event.objects.filter(condition).all()]
    )
    # print("active channels", active_channels)
    if len(active_channels) == 0:
        return None, None, None

    # TODO: implement load balancing
    return (
        list(active_channels)[0],
        user_candidate_channels[list(active_channels)[0]][0],
        user_candidate_channels[list(active_channels)[0]][1],
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def handle_result(request):
    """Result posted from host in response to query"""
    if "qid" not in request.data or "result" not in request.data:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        # find the record corresponding to the request
        record = QueryRecord.objects.filter(pk=request.data.get("qid")).first()
        if record.status == "done":
            return Response(
                {"detail": "query already completed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        query_consumer_channel = find_query_consumer_channel(record)
        if not query_consumer_channel:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # send response to the client
        dje.send_event(
            query_consumer_channel,
            "message",
            {
                "qid": record.id,
                "result": request.data.get("result"),
                "cluster": record.cluster.name,
                "producer": record.producer.username,
            },
        )

        # update query record status in db
        record.status = "done"
        record.save()

        return Response(status=status.HTTP_200_OK)


def find_query_consumer_channel(record) -> str:
    """Find active consumer channel to forward query result back to.

    :param record: Status of the query being returned.
    :type record: models.QueryRecord
    :return: Channel name.
    :rtype: str
    """

    # want to check that the channel is open for the user
    token, created = Token.objects.get_or_create(user=record.consumer)
    candidate_channel = f"consumer-{token.key}"

    # expecting a single channel to be found
    active_consumer_channel = dje.models.Event.objects.filter(
        channel__startswith=candidate_channel
    ).first()

    if not active_consumer_channel:
        return None

    return active_consumer_channel.channel


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def ping(request):
    return Response({"ping": "pong"}, status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def seek_result(request):
    """Client coming back for the result to their queries.
    DEPRECATED"""
    if "qid" not in request.data:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    elif request.data.get("qid") not in QUERY_STORE:
        return Response(status=status.HTTP_404_NOT_FOUND)
    elif (
        request.data.get("qid") in QUERY_STORE
        and not QUERY_STORE[request.data.get("qid")]
    ):
        return Response(
            {"pending": "awaiting result"}, status=status.HTTP_400_BAD_REQUEST
        )
    else:
        return Response(
            {"result": QUERY_STORE[request.data.get("qid")]}, status=status.HTTP_200_OK
        )
