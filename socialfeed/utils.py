import re
from .models import Hashtag, PostHashtag, Mention, Notification, NOTIF_TYPES
from django.contrib.auth.models import User

HASHTAG_RE = re.compile(r'#(\w+)')
MENTION_RE = re.compile(r'@(\w+)')
YOUTUBE_RE = re.compile(r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w\-]{11})')

def extract_youtube_id(text: str) -> str:
    m = YOUTUBE_RE.search(text or '')
    return m.group(1) if m else ''

def handle_hashtags(post):
    tags = set(HASHTAG_RE.findall(post.content or ''))
    for t in tags:
        tag, _ = Hashtag.objects.get_or_create(name=t.lower())
        PostHashtag.objects.get_or_create(post=post, hashtag=tag)

def handle_mentions_on_post(post):
    usernames = set(MENTION_RE.findall(post.content or ''))
    for uname in usernames:
        try:
            u = User.objects.get(username__iexact=uname)
            Mention.objects.create(mentioned_user=u, post=post)
            if u != post.user:
                Notification.objects.create(user=u, actor=post.user, post=post, notif_type='mention_post')
        except User.DoesNotExist:
            continue

def handle_mentions_on_reply(reply):
    usernames = set(MENTION_RE.findall(reply.content or ''))
    for uname in usernames:
        try:
            u = User.objects.get(username__iexact=uname)
            Mention.objects.create(mentioned_user=u, reply=reply)
            if u != reply.user:
                Notification.objects.create(user=u, actor=reply.user, reply=reply, notif_type='mention_reply')
        except User.DoesNotExist:
            continue
