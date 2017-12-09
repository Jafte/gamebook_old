from django.http import Http404
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.base import ContextMixin
from game.models import Game


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
