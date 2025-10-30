from django.contrib import admin
from .models import Skill
from .models import UserProfile, Post, Reply, Follow, Hashtag, PostHashtag, PostLike, ReplyLike, Mention, Notification

admin.site.register([UserProfile, Post, Reply, Follow, Hashtag, PostHashtag, PostLike, ReplyLike, Mention, Notification])

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)