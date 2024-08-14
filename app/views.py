from django.shortcuts import render, redirect
import instaloader
from django.http import JsonResponse, HttpResponse
import requests
import os

# Create your views here.

def home(request):

    # Create an instance of Instaloader
    L = instaloader.Instaloader()

    error_message = ""

    # Log in to Instagram
    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            L.login(username, password)
            
            session_directory = f"{os.getcwd()}/static/"
            session_file = os.path.join(session_directory, f"{username}")
            L.save_session_to_file(session_file)

            print("Logged in successfully!")

            request.session["is_user_logged_in"] = True

            profile = instaloader.Profile.from_username(L.context, username)

            request.session['logged_user'] = profile.username
            request.session['logged_user_id'] = profile.userid
            request.session['posts'] = profile.mediacount
            request.session['followers'] = profile.followers
            request.session['followees'] = profile.followees
            request.session['bio'] = profile.biography
            request.session['profile_pic_url'] = profile.profile_pic_url
            request.session['session_file'] = session_file


            response = requests.get(profile.profile_pic_url)
            if response.status_code == 200:
                with open('static/profile_pics/profile_picture.jpg', 'wb') as file:
                    file.write(response.content)
                print("Image downloaded successfully.")

            return redirect("app:user_dashboard")
        
        except instaloader.exceptions.BadCredentialsException:
            error_message = "Invalid username or password"
            print("Invalid username or password.")
        except instaloader.exceptions.TwoFactorAuthRequiredException:
            error_message = "Two-factor authentication is required."
            print("Two-factor authentication is required.")
        except Exception as e:
            error_message = f"An error occurred: {e}"
            print(f"An error occurred: {e}")

    return render(request, 'home.html', {
        "error_message": error_message
    })


def user_dashboard(request):

    L = instaloader.Instaloader()
    L.load_session_from_file(f"{request.session.get('logged_user')}", request.session.get('session_file'))
    
    if request.session.get("is_user_logged_in") == False:
        return HttpResponse("User is not logged in")

    user_username = request.session.get("logged_user")
    user_user_id = request.session.get("logged_user_id")
    post_count = request.session.get("posts")
    user_followers = request.session.get("followers")
    user_followees = request.session.get("followees")
    user_bio = request.session.get("bio")
    user_profile_pic = request.session.get("profile_pic_url")
    

    return render(request, 'dashboard.html', {
        "user_username": user_username,
        "user_followers": user_followers,
        "user_followees": user_followees,
        "user_profile_pic": user_profile_pic,
        "user_bio": user_bio,
        "user_user_id": user_user_id,
        "post_count": post_count
    })


def logout(request):
    request.session["is_user_logged_in"] = False
    return render(request, 'logout.html', {})


def search(request):
    L = instaloader.Instaloader()
    L.load_session_from_file(f"{request.session.get('logged_user')}", request.session.get('session_file'))

    if request.session.get("is_user_logged_in") == False:
        return HttpResponse("User is not logged in")
    
    if os.path.exists("static/profile_pics/searched_user_profile_pic.jpg"):
        os.remove("static/profile_pics/searched_user_profile_pic.jpg")
    
    username = ""
    profile_pic = ""
    user_id = ""
    post_count = ""
    followers = ""
    followings = ""
    bio = ""
    error = False
    post_list = []
    post_list_empty = False
    error_message = ""
    is_private = False
    
    if request.method == "POST":
        try:
            searched_user = request.POST.get("searched_user")
            
            profile = instaloader.Profile.from_username(L.context, searched_user)

            response = requests.get(profile.profile_pic_url)
            if response.status_code == 200:
                with open('static/profile_pics/searched_user_profile_pic.jpg', 'wb') as file:
                    file.write(response.content)

            for post in profile.get_posts():

                post_list.append({
                    "post_url": post.shortcode,
                    "caption": post.caption,
                    "posted_on": post.date,
                    "likes": post.likes,
                    "comments": post.comments,
                    "image_url": post.url
                })

            print("POST LIST: ", post_list)

            username = profile.username
            profile_pic = profile.profile_pic_url
            user_id = profile.userid
            post_count = profile.mediacount
            followers = profile.followers
            followings = profile.followees
            bio = profile.biography
            if post_count > 0 and len(post_list) == 0:
                is_private = True

        except Exception as e:
            error_message = f"{e}"
            print("ERROR: ", e)
            error = True
    
    return render(request, 'search.html', {
        "username": username,
        "profile_pic": profile_pic,
        "user_id": user_id,
        "post_count": post_count,
        "followers": followers,
        "followings": followings,
        "bio": bio,
        "post_list": post_list,
        "error": error,
        "post_list_empty": post_list_empty,
        "error_message": error_message,
        "is_private": is_private
    })