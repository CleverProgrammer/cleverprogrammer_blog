from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment
from .form import PostForm, CommentForm, UserForm
from mysite.settings import STRIPE_API_TEST_SK, STRIPE_API_TEST_PK, STRIPE_API_LIVE_PK, STRIPE_API_LIVE_SK
from notifications.views import AllNotificationsList, UnreadNotificationsList, live_unread_notification_list

import stripe

stripe.api_key = STRIPE_API_LIVE_SK


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
        {'stripe_test_api_pk': STRIPE_API_LIVE_PK}
    )


@user_passes_test(lambda user: user.is_superuser)
def dashboard(request):
    """
    All student invoices and homework assignemnts will be viewed from here.
    """
    # customers = stripe.SubscriptionItem.list(subscription='sub_AW77u4xuqfsC4g')
    # customer['subscriptions']['data'][0]['id']
    starting_after = None
    all_customers = []
    while True:
        customers = stripe.Customer.list(limit=100, starting_after=starting_after)
        print(starting_after)
        if len(customers.data) == 0:
            break
        for customer in customers:
            all_customers.append(customer)
        starting_after = customers.data[-1].id
    print(len(all_customers))
    # print(all_customers[0]['subscriptions']['data'][0]['id'])
    # print(all_customers[0]['subscriptions']['data'][0]['id'])
    final_customers = []
    # final_customers = all_customers[0]
    # for customer in all_customers:
    #     try:
    #         if customer['subscriptions']['data'][0]['id'] == "sub_AW77u4xuqfsC4g":
    #             final_customers.append(customer)
    #     except IndexError:
    #         pass
    #
    # print(stripe.Subscription.list(limit=10))
    all_subs = []
    for customer in all_customers:
        # print(customer.id, customer.subscriptions)
        if customer.subscriptions.data:
            all_subs.append((customer.email, customer.subscriptions.data[0].plan.amount / 100))
    mrr = 0
    for customer, amount in all_subs:
        mrr += amount

    # all_subs = stripe.Subscription.list(status='active')

    # for customer in all_customers:
    #     print(stripe.Subscription.list(status='active', customer=customer.id))

    # all_subs =
    # final_customers = [customer for customer in all_customers if
    # customer['subscriptions']['data'][0]['id'] == "sub_AW77u4xuqfsC4g"]
    # acm_students = [customer['data'][0]['subscriptions']['data'][0]['id'] for customer in all_customers]

    # customers = stripe.Customer.list(limit=25, include=['total_count'])
    # print(customers.total_count)
    return render(request, 'blog/students/dashboard.html', {'customers': all_subs, 'mrr': mrr})


@login_required
def my_profile(request):
    """
    User profiles with ability to change avatars
    """
    return render(request, 'blog/students/profile.html')
