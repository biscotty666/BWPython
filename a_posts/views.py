from django.shortcuts import render, redirect
from .models import *
from django.forms import ModelForm
from django import forms
from bs4 import BeautifulSoup
import requests
from django.contrib import messages

def home_view(request):
    posts = Post.objects.all()
    return render(request, "a_posts/home.html", { 'posts' : posts})

def post_create_view(request):
    return render(request, 'a_posts/post_create.html')

class PostCreateForm(ModelForm):
    class Meta:
        model = Post
        fields = ['url', 'body']
        labels = {
            'body' : 'Caption'
        }
        widgets = {
            'body' : forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a caption...', 'class': 'font1 text-4xl'}),
            'url' : forms.TextInput(attrs={'placeholder': 'Add url ...'}),
        }
        
def post_create_view(request):
    form = PostCreateForm()
    
    if request.method == 'POST':
        # form = PostCreateForm(request.POST)
        #     if request.method == 'POST':
        form = PostCreateForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            
            website = requests.get(form.data['url'])
            sourcecode = BeautifulSoup(website.text, 'html.parser')
            find_image = sourcecode.select('meta[content^="https://live.staticflickr.com/"]')
            # try:   
            image = find_image[0]['content']
            # except:
                # messages.error(request, 'Requested image is not on Flickr!')
                # return redirect('post-create')
            
            post.image = image
            
            find_title = sourcecode.select('h1.photo-title')
            title = find_title[0].text.strip()
            post.title = title
            
            find_artist = sourcecode.select('a.owner-name')
            artist = find_artist[0].text.strip() 
            post.artist = artist
            
            post.author = request.user
            
            post.save()
            # form.save_m2m()
            return redirect('home')
        
    return render(request, 'a_posts/post_create.html', { 'form' : form })

def post_delete_view(request, pk):
    post = Post.objects.get(id=pk)
    
    if request.method == "POST":
        post.delete()
        messages.success(request, 'Post deleted')
        return redirect('home')
    
    return render(request, 'a_posts/post_delete.html', {'post' : post})




