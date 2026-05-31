from django.contrib import admin
from .models import (
    Issue,
    Comment,
    IssueImage,
    CommentImage,
    Notification
)

admin.site.register(Issue)
admin.site.register(Comment)
admin.site.register(IssueImage)
admin.site.register(CommentImage)
admin.site.register(Notification)
