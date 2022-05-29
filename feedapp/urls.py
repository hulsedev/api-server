from django.urls import path

from feedapp import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("cluster/leave/", views.leave_cluster, name="leave_cluster"),
    path("cluster/delete/", views.delete_cluster, name="delete_cluster"),
    path("cluster/edit/", views.edit_cluster, name="edit_cluster"),
    path("cluster/join/", views.join_cluster, name="join_cluster"),
    path("clusters/", views.get_clusters, name="clusters"),
    path("ping/", views.ping, name="ping"),
    path("cluster/create/", views.create_cluster, name="create_cluster"),
    path("callback/", views.callback, name="callback"),
]
