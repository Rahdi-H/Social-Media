from django.contrib import admin
from .models import Profile, Post, PostLike, FollowersCount

# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'id_user', 'bio', 'profileimg', 'location']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['user', 'image', 'caption', 'created_at', 'no_of_likes']

@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['post_id', 'username']

@admin.register(FollowersCount)
class FollowersCountAdmin(admin.ModelAdmin):
    list_display = ['follower', 'user']