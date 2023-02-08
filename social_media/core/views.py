from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib import messages
from .models import Profile, Post, PostLike, FollowersCount
import random
from itertools import chain

# Create your views here.
@login_required()
def index(request):
    user_profile = Profile.objects.get(user=request.user)
    user_following_list = []
    feed_list = []
    user_following = FollowersCount.objects.filter(follower=request.user.username)
    for i in user_following:
        user_following_list.append(i)
    for username in user_following_list:
        feed = Post.objects.filter(user=username.user)
        feed_list.append(feed)
    fee = list(chain(*feed_list))
    # user suggestions start
    all_users = User.objects.all()
    user_following_l = []
    for user in user_following:
        user_l = User.objects.filter(username=user.user)
        user_following_l.append(user_l)
    new_suggestions_list = [i for i in list(all_users) if (i not in list(user_following_l))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [i for i in list(new_suggestions_list) if (i not in list(current_user))]
    random.shuffle(final_suggestions_list)

    username_profile = []
    username_profile_list = []
    for id in final_suggestions_list:
        username_profile.append(id.id)
    for i in username_profile:
        new_profile = Profile.objects.filter(id_user=i)
        username_profile_list.append(new_profile)
    profile_list = list(chain(*username_profile_list))
    context = {
        'posts' : fee,
        'user_profile': user_profile,
        'profile_list': profile_list[:4]
    }
    return render(request, 'index.html', context)

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.warning(request, "An user with this email exists")
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.warning(request, "An user with this username exists")
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                user_model = User.objects.get(username = username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                return redirect('settings')
        else:
            messages.warning(request, "password didn't matched")
            return redirect('signup')
    else:
        return render(request, 'signup.html')
    
def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.warning(request, "username or password didn't matched")
            return redirect('signin')
    else:
        return render(request, 'signin.html')
    
@login_required()
def signout(request):
    auth.logout(request)
    return redirect('signin')

@login_required()
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']
            user_profile.profileimg = image
            user_profile.bio = bio 
            user_profile.location = location
            user_profile.save()
            return redirect('settings')
        if request.FILES.get('image') != None:
            image = request.FILES['image']
            bio = request.POST['bio']
            location = request.POST['location']
            user_profile.profileimg = image
            user_profile.bio = bio 
            user_profile.location = location
            user_profile.save()
            return redirect('settings')
    else:
        return render(request, 'settings.html', {'user_profile':user_profile})
    
@login_required()
def add_post(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        user = request.user.username
        image = request.FILES.get('image')
        caption = request.POST['caption']
        new_post = Post(user=user, image=image, caption=caption)
        new_post.save()
        return redirect('index')

    return render(request, 'add_post.html', {'user_profile':user_profile})

@login_required()
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id=post_id)
    like_filter = PostLike.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = PostLike.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        post.save()
        return redirect('index')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
        return redirect('index')

@login_required()
def profile(request, pk):
    user_profile = Profile.objects.get(user=request.user)
    user_object = User.objects.get(username=pk)
    visitor_user_profile = Profile.objects.get(user=request.user)
    main_user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=user_object.username)
    follower = request.user.username
    user = pk
    print(follower)
    print(user)
    print(FollowersCount.objects.filter(follower=follower, user=user).first())
    if FollowersCount.objects.filter(follower=follower, user=user).first() != None:
        button_text = 'Unfollow'
    else:
        button_text = "Follow"

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))
    context = {
        'user_object' : user_object,
        'visitor_user_profile' : visitor_user_profile,
        'main_user_profile' : main_user_profile,
        'user_posts' : user_posts,
        'button_text' : button_text,
        'user_followers' : user_followers,
        'user_following' : user_following,
        'user_profile' : user_profile
    }
    return render(request, 'profile.html', context)

@login_required
def follow(request, username):
    follower = request.user.username
    user = username
    print(follower)
    print(user)
    if FollowersCount.objects.filter(follower=follower, user=user).first():
        old_follower = FollowersCount.objects.filter(follower=follower, user=user).first()
        old_follower.delete()
        return redirect('profile', user)
    else:
        new_follower = FollowersCount.objects.create(follower=follower, user=user)
        new_follower.save()
        return redirect('profile', user)

@login_required
def search(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains = username)

        username_profile = []
        username_profile_list = []
        for user in username_object:
            username_profile.append(user.id)
        for id in username_profile:
            profile_list = Profile.objects.filter(id_user= id)
            username_profile_list.append(profile_list)
        username_profile_list = list(chain(*username_profile_list))
    context = {
        'user_profile' : user_profile,
        'username_profile_list' : username_profile_list,
    }
    return render(request, 'search.html', context)