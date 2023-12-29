from django.shortcuts import render

def home_view(request):
    print(request)
    print(request.method)
    return render(request, "a_posts/home.html")