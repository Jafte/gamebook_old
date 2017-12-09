from django.http import Http404
from django.urls import reverse
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.base import ContextMixin
from game.models import Game, Character


class GameMixin(ContextMixin):
    game_pk_url_kwarg = 'game_pk'
    game = None

    def get_context_data(self, **kwargs):
        context = {
            'game': self.game
        }
        context.update(kwargs)
        return super().get_context_data(**context)

    def get_game(self):
        queryset = Game.objects.filter(author=self.request.user)

        pk = self.kwargs.get(self.game_pk_url_kwarg, None)
        queryset = queryset.filter(pk=pk)

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj


class DetailWithGameView(GameMixin, DetailView):
    def get(self, request, *args, **kwargs):
        self.game = self.get_game()
        return super().get(request, *args, **kwargs)


class DeleteWithGameView(DetailWithGameView, DeleteView):
    def get_success_url(self):
        return self.game.get_absolute_url()

    def post(self, request, *args, **kwargs):
        self.game = self.get_game()
        return super().post(request, *args, **kwargs)


class CreateWithGameView(GameMixin, CreateView):
    def get(self, request, *args, **kwargs):
        self.game = self.get_game()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.game = self.get_game()
        return super().post(request, *args, **kwargs)


class UpdateWithGameView(GameMixin, UpdateView):
    def get(self, request, *args, **kwargs):
        self.game = self.get_game()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.game = self.get_game()
        return super().post(request, *args, **kwargs)


class IndexView(TemplateView):
    template_name = 'index.html'


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


class CharacterDetailView(LoginRequiredMixin, DetailWithGameView):
    template_name = 'game/charatcer/detail.html'
    model = Character
    pk_url_kwarg = 'character_pk'


class CharacterCreateView(LoginRequiredMixin, CreateWithGameView):
    template_name = 'game/charatcer/form.html'
    model = Character
    fields = ['name', 'description']

    def form_valid(self, form):
        if self.game.can_create_new_character():
            self.object = form.save(commit=False)
            self.object.game = self.game
            self.object.save()
            return super().form_valid(form)
        else:
            return redirect(self.game.get_absolute_url())


class CharacterUpdateView(LoginRequiredMixin, UpdateWithGameView):
    template_name = 'game/charatcer/form.html'
    model = Character
    pk_url_kwarg = 'character_pk'
    fields = ['name', 'description']


class CharacterDeleteView(LoginRequiredMixin, DeleteWithGameView):
    template_name = 'game/charatcer/delete.html'
    model = Character
    pk_url_kwarg = 'character_pk'
