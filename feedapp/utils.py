from feedapp import models


def select_cluster(user):
    # TODO: implement least served cluster selection logic
    return user.clusters.first()
