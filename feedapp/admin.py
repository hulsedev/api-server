from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Cluster, QueryRecord

admin.site.register(User, UserAdmin)
admin.site.register(Cluster)
admin.site.register(QueryRecord)
