from datetime import datetime
from typing import Any, Dict

import pytz
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from blog.models import Category, Comment, Post
from blogicum.constants import const

from .forms import CommentForm, PostForm, UserForm


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = const.PAGE_LIMIT

    queryset = (
        Post.objects
            .select_related(
                'category',
                'author',
                'location'
            ).order_by('-pub_date')
             .annotate(comment_count=Count('comments'))
             .filter(
                pub_date__lte=datetime.now(
                    tz=pytz.timezone('Europe/Moscow')
                ),
                is_published=True,
                category__is_published=True
                )
    )


class CategoryPostListView(ListView):
    model = Category
    paginate_by = const.PAGE_LIMIT
    template_name = 'blog/category.html'

    def get_queryset(self) -> QuerySet[Any]:
        category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug']
        )
        return (
            category
            .category_post
            .select_related(
                'category',
                'author',
                'location'
            )
            .filter(category__is_published=True)
            .filter(
                category_id=category.id,
                is_published=True,
                pub_date__lte=datetime.now(tz=pytz.timezone('Europe/Moscow')),
                category__is_published=True
            ).order_by('-pub_date')
            .annotate(comment_count=Count('comments'))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = get_object_or_404(
            Category.objects
            .filter(
                slug=self.kwargs['category_slug'],
                is_published=True
                )
        )
        return context


class PostDetailDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def dispatch(
            self,
            request: HttpRequest,
            *args: Any,
            **kwargs: Any
         ) -> HttpResponse:
        post_detail = get_object_or_404(Post, pk=kwargs['pk'])
        if (
            not (
                post_detail.is_published
                and post_detail.category.is_published)
                or post_detail.pub_date >= datetime.now(
                    tz=pytz.timezone('Europe/Moscow'))
                ) and post_detail.author != request.user:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        context['form'] = CommentForm()
        return context


class CreatePostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args: Any, **kwargs: Any) -> HttpResponse:
        post_to_edit = get_object_or_404(Post, pk=kwargs['pk'])
        if post_to_edit.author == request.user:
            return super().dispatch(request, *args, **kwargs)
        return redirect('blog:post_detail', pk=kwargs['pk'])

    def get_success_url(self) -> str:
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.pk})


class PostDeleteDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def dispatch(
            self,
            request: HttpRequest,
            *args: Any,
            **kwargs: Any
         ) -> HttpResponse:
        post_to_delete = get_object_or_404(Post, pk=kwargs['pk'])
        if post_to_delete.author == request.user or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        return redirect('blog:post_detail', pk=kwargs['pk'])

    def get_success_url(self) -> str:
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class AddCommentCreateView(LoginRequiredMixin, CreateView):
    main_post = None
    template_name = 'blog/detail.html'
    model = Comment
    form_class = CommentForm

    def dispatch(
            self,
            request: HttpRequest,
            *args: Any, **kwargs: Any
         ) -> HttpResponse:
        self.main_post = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def post(
            self,
            request: HttpRequest,
            *args: str,
            **kwargs: Any
         ) -> HttpResponse:
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.post = self.main_post
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.object.post.pk}
        )


class EditCommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'id'

    def dispatch(self, request, *args: Any, **kwargs: Any) -> HttpResponse:
        comment_to_edit = get_object_or_404(Comment, pk=kwargs['id'])
        if comment_to_edit.author == request.user or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        return redirect('blog:post_detail', pk=kwargs['pk'])

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        return context

    def get_object(self) -> QuerySet[Any]:
        return Comment.objects.get(pk=self.kwargs['id'])

    def get_success_url(self) -> str:
        self.pk = self.object.post.id
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.pk})


class DeleteCommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def dispatch(
            self,
            request: HttpRequest,
            *args: Any,
            **kwargs: Any
         ) -> HttpResponse:
        comment_to_delete = get_object_or_404(Comment, pk=kwargs['id'])
        if (
            comment_to_delete.author == request.user
            or request.user.is_superuser
             ):
            return super().dispatch(request, *args, **kwargs)
        return redirect('blog:post_detail', pk=kwargs['pk'])

    def get_success_url(self) -> str:
        self.pk = self.object.post.id
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.pk})


class EditProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'
    slug_url_kwarg = 'username'

    def dispatch(
            self,
            request: HttpRequest,
            *args: Any,
            **kwargs: Any
         ) -> HttpResponse:
        if kwargs['username'] == request.user.username:
            return super().dispatch(request, *args, **kwargs)
        return redirect('blog:profile', username=kwargs['username'])

    def get_object(self) -> QuerySet[Any]:
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_success_url(self) -> str:
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.object.username}
        )


class ProfileInfoTemplateView(ListView):
    model = User
    paginate_by = const.PAGE_LIMIT
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User, username=self.kwargs['username']
        )
        return context

    def get_queryset(self) -> QuerySet[Any]:
        author = get_object_or_404(User, username=self.kwargs['username'])
        return (
            author
            .author_post.select_related(
                'category',
                'author',
                'location')
            .order_by('-pub_date')
            .annotate(comment_count=Count('comments'))
        )
