from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment
from .form import PostForm, CommentForm, UserForm
from mysite.settings import STRIPE_API_TEST_SK, STRIPE_API_TEST_PK
from notifications.views import AllNotificationsList, UnreadNotificationsList, live_unread_notification_list

import stripe

stripe.api_key = STRIPE_API_TEST_SK


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})


@login_required
def my_unread_notifications(request):
    my_unreads = request.user.notifications.unread()
    # live_unreads = live_unread_notification_list(request)
    return render(request, 'blog/unread_notifications.html', {'my_unreads': my_unreads})


@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)


def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('post_detail', pk=comment.post.pk)


@login_required
def post_new(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})


@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    return render(request, 'blog/post_draft_list.html', {'posts': posts})


@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)


@user_passes_test(lambda user: user.is_anonymous)
def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = User.objects.create_user(**form.cleaned_data)
            login(request, new_user)
            return HttpResponseRedirect('/')
    else:
        form = UserForm()
    return render(
        request,
        'blog/registration/signup.html',
        {'form': form}
    )


def checkout(request):
    if request.method == 'POST':
        token = request.POST['stripeToken']
        charge = stripe.Charge.create(
            amount=99,
            currency='usd',
            description='Example charge',
            source=token,
        )
        return HttpResponseRedirect('/')
    return render(
        request,
        'blog/checkout/checkout.html',
        {'stripe_test_api_pk': STRIPE_API_TEST_PK}
    )


@user_passes_test(lambda user: user.is_superuser)
def dashboard(request):
    """
    All student invoices and homework assignemnts will be viewed from here.
    """
    customers = stripe.Customer.list()
    return render(request, 'blog/students/dashboard.html', {'customers': customers})


@login_required
def my_profile(request):
    """
    User profiles with ability to change avatars
    """
    return render(request, 'blog/students/profile.html')
