from datetime import datetime
from urllib.parse import quote_plus, urlencode

from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
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

from .models import Cluster, User

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
    if (
        request.session.get("user")
        and not isinstance(request.user, AnonymousUser)
        and not request.session.get("is_desktop")
    ):
        return redirect(request.build_absolute_uri(reverse("index")))
    elif (
        request.session.get("user")
        and not isinstance(request.user, AnonymousUser)
        and request.session.get("is_desktop")
    ):
        # redirect to local server
        token, created = Token.objects.get_or_create(user=request.user)
        return redirect(
            f"{settings.HULSE_DESKTOP_URL}?"
            + urlencode(
                {
                    "authToken": token.key,
                },
                quote_via=quote_plus,
            ),
        )

    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token
    return redirect(request.build_absolute_uri("/login/auth0"))


def login(request):
    """Login through Auth0."""
    # register whether the app comes from the web or desktop
    request.session["is_desktop"] = request.GET.get("source") == "desktop"

    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
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
    if not cluster or request.user != cluster.admin:
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
    if not cluster or request.user != cluster.admin:
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
    if not cluster or cluster.deleted or request.user not in cluster.members.all():
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
    if not cluster or cluster.deleted or request.user in cluster.members.all():
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


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def ping(request):
    return Response({"ping": "pong"}, status=status.HTTP_200_OK)
