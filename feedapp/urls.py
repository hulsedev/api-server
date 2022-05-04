import django_eventstream
from django.urls import include, path

from feedapp import views, events

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "consumer/<member_id>/",
        events.handle_consumer_event,
        {"format-channels": ["consumer-{member_id}"]},
    ),
    path(
        "producer/<member_id>/",
        events.handle_producer_event,
        {"format-channels": ["producer-{member_id}"]},
    ),
    path("login/", views.login, name="login"),
    path("result/", views.handle_result, name="handle_result"),
    path("query/", views.query, name="query"),
    path("logout/", views.logout, name="logout"),
    path("result/retrieve/", views.seek_result, name="seek_result"),
    path("cluster/leave/", views.leave_cluster, name="leave_cluster"),
    path("cluster/delete/", views.delete_cluster, name="delete_cluster"),
    path("cluster/edit/", views.edit_cluster, name="edit_cluster"),
    path("cluster/join/", views.join_cluster, name="join_cluster"),
    path("clusters/", views.get_clusters, name="clusters"),
    path("ping/", views.ping, name="ping"),
    path("cluster/create/", views.create_cluster, name="create_cluster"),
    path("callback/", views.callback, name="callback"),
]
