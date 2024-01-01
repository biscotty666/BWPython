from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from bs4 import BeautifulSoup
import requests
from django.contrib import messages

def home_view(request, tag=None):
    if tag:
        posts = Post.objects.filter(tags__slug=tag)
        tag = get_object_or_404(Tag, slug=tag)
    else:
        posts = Post.objects.all()
        
    categories = Tag.objects.all()
    
    context = {
        'posts': posts,
        'categories': categories,
        'tag': tag,
    }
    return render(request, "a_posts/home.html", context)

@login_required
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
            print(find_title)
            title = find_title[0].text.strip()
            post.title = title
            
            find_artist = sourcecode.select('a.owner-name')
            artist = find_artist[0].text.strip() 
            post.artist = artist
            
            post.author = request.user
            
            post.save()
            form.save_m2m()
            return redirect('home')
        
    return render(request, 'a_posts/post_create.html', { 'form': form })

@login_required
def post_delete_view(request, pk):
    post = get_object_or_404(Post, id=pk, author=request.user)
    
    if request.method == "POST":
        post.delete()
        messages.success(request, 'Post deleted')
        return redirect('home')
    
    return render(request, 'a_posts/post_delete.html', {'post': post})

@login_required
def post_edit_view(request, pk):
    post = get_object_or_404(Post, id=pk, author=request.user)
    form = PostEditForm(instance=post)
    
    if request.method == "POST":
        form = PostEditForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated")
            return redirect('home')
        
    context = {
       'post': post,
       'form': form 
    }
    print(f'context: {context}')
    return render(request, 'a_posts/post_edit.html', context)

def post_page_view(request, pk):
    post = get_object_or_404(Post, id=pk)
    
    commentform = CommentCreateForm()
    
    context = {
        'post': post,
        'commentform': commentform
    }
    
    return render(request, 'a_posts/post_page.html', context)

@login_required
def comment_sent(request, pk):
    post = get_object_or_404(Post, id=pk)
    
    if request.method == 'POST':
        form = CommentCreateForm(request.POST)
        if form.is_valid:
            comment = form.save(commit=False)
            comment.author = request.user
            comment.parent_post = post
            comment.save()
            
    return redirect('post', post.id)

@login_required
def comment_delete_view(request, pk):
    post = get_object_or_404(Comment, id=pk, author=request.user)
    
    if request.method == "POST":
        post.delete()
        messages.success(request, 'Comment deleted')
        return redirect('post', post.parent_post.id)
    
    return render(request, 'a_posts/comment_delete.html', {'comment': post})

