import django_eventstream as dje
from django.conf import settings
from loguru import logger
from django_eventstream.channelmanager import DefaultChannelManager
from rest_framework.authtoken.models import Token

from feedapp import models, views


class ChannelAuthManager(DefaultChannelManager):
    def can_read_channel(self, user, channel):
        try:
            role, token_str = channel.split("-")
        except Exception as e:
            return False

        # check if role is ok
        if role not in ["consumer", "producer"] or not token_str:
            return False

        # check if user is valid
        print(token_str)
        user = Token.objects.get(key=token_str).user
        if not user:
            return False

        return True

    def get_channels_for_request(self, request, view_kwargs):
        # by default, use view keywords, else query params
        if "format-channels" in view_kwargs:
            channels = set()
            for format_channel in view_kwargs["format-channels"]:
                channels.add(format_channel.format(**view_kwargs))
        elif "channels" in view_kwargs:
            channels = set(view_kwargs["channels"])
        elif "channel" in view_kwargs:
            channels = set([view_kwargs["channel"]])
        else:
            channels = set(request.GET.getlist("channel"))

        # in case handling consumer request
        if view_kwargs.get("format-channels")[0].startswith("consumer"):
            _ = self.handle_query_request(request, view_kwargs)
            self.add_artificial_welcome_event("consumer", channels)
        else:
            logger.debug("Received producer request")
            # artificially add a welcome event when producer logs in
            self.add_artificial_welcome_event("producer", channels)

        return channels

    def add_artificial_welcome_event(self, welcome_type, channels):
        storage_backend = dje.utils.get_storage()
        if len(channels) > 1:
            raise RuntimeError(
                "Why are there more than 1 channels? {}".format(channels)
            )
        else:
            channel = list(channels)[0]

        # already in the channel manager, and assume that storage activated
        event_data = {f"hello {welcome_type}": f"{channel}"}
        e = storage_backend.append_event(channel, "welcome", event_data)
        # pub_id = str(e.id)
        # pub_prev_id = str(e.id - 1)

        # TODO: check if publishing to listener managers is necessary
        listener_manager = dje.consumers.get_listener_manager()
        listener_manager.add_to_queues(channel, e)

        # NOTE: can skip the publication step since artificial event, local

    def handle_query_request(self, request, view_kwargs) -> bool:
        logger.debug("Received query request")
        user = Token.objects.get(key=view_kwargs.get("member_id")).user
        if not user or not self.check_consumer_inputs(request):
            print("invalid user or request")
            return False

        # find an active producer channel for this consumer query (shared cluster)
        producer_channel, cluster, producer = views.find_active_channel(user)
        if not producer_channel:
            return False

        # acknowledge query since found an active producer
        record = models.QueryRecord(
            task=request.GET.get("task"),
            status="pending",
            consumer=user,
            producer=producer,
            cluster=cluster,
        )
        record.save()

        # send event to producer channel for query
        dje.send_event(
            producer_channel,
            "message",
            {
                "task": request.GET.get("task"),
                "data": request.GET.get("data"),
                "qid": record.id,
            },
        )

        return True

    def check_consumer_inputs(self, request):
        # make sure have both data and task
        return request.GET.get("task") in settings.SUPPORTED_TASKS and request.GET.get(
            "data"
        )
