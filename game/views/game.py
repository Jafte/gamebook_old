from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from game.models import Game


class GameListView(LoginRequiredMixin, ListView):
    template_name = 'game/list.html'
    model = Game

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(author=self.request.user)


class GameDetailView(LoginRequiredMixin, DetailView):
    template_name = 'game/detail.html'
    model = Game
    pk_url_kwarg = 'game_pk'


class GameCreateView(LoginRequiredMixin, CreateView):
    template_name = 'game/form.html'
    model = Game
    fields = ['name', 'description']

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        return super().form_valid(form)


class GameUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'game/form.html'
    model = Game
    pk_url_kwarg = 'game_pk'
    fields = ['name', 'description']


class GameDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'game/delete.html'
    model = Game
    pk_url_kwarg = 'game_pk'

    def get_success_url(self):
        return reverse('game_list')
