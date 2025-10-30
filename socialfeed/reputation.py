# socialfeed/reputation.py
from django.contrib.auth.models import User
from socialfeed.models import PostLike, ReplyLike, Follow, Post, UserProfile


def update_user_reputations():
    # Erst alle auf 0
    UserProfile.objects.update(reputation=0)

    for user in User.objects.all():
        profile = user.profile

        # Likes erhalten
        post_likes = PostLike.objects.filter(post__user=user).count()
        reply_likes = ReplyLike.objects.filter(reply__user=user).count()

        # Followers erhalten
        followers = Follow.objects.filter(following=user).count()

        # Eigene Posts
        posts = Post.objects.filter(user=user).count()

        # Reposts erhalten
        reposts_received = Post.objects.filter(original_post__user=user).count()

        # Gewichtung
        reputation = (
            post_likes * 2 +
            reply_likes * 1 +
            followers * 3 +
            posts * 1 +
            reposts_received * 2
        )

        profile.reputation = reputation
        profile.save(update_fields=['reputation'])
