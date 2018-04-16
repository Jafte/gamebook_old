from django.http import Http404
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.base import ContextMixin
from game.models import Game, Scene


class GameMixin(ContextMixin):
    game_pk_url_kwarg = 'game_pk'
    game = None

    def get_context_data(self, **kwargs):
        context = {
            'game': self.get_game()
        }
        context.update(kwargs)
        return super().get_context_data(**context)

    def get_game(self):
        if not self.game:
            queryset = Game.objects.filter(author=self.request.user)

            pk = self.kwargs.get(self.game_pk_url_kwarg, None)
            queryset = queryset.filter(pk=pk)

            try:
                # Get the single item from the filtered queryset
                self.game = queryset.get()
            except queryset.model.DoesNotExist:
                raise Http404(
                    _("No %(verbose_name)s found matching the query") %
                    {'verbose_name': queryset.model._meta.verbose_name}
                )

        return self.game


class DetailWithGameView(GameMixin, DetailView):
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class DeleteWithGameView(DetailWithGameView, DeleteView):
    def get_success_url(self):
        game = self.get_game()
        return game.get_absolute_url()

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CreateWithGameView(GameMixin, CreateView):
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UpdateWithGameView(GameMixin, UpdateView):
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class SceneMixin(GameMixin):
    scene_pk_url_kwarg = 'scene_pk'
    scene = None

    def get_context_data(self, **kwargs):
        context = {
            'scene': self.get_scene()
        }
        context.update(kwargs)
        return super().get_context_data(**context)

    def get_scene(self):
        if not self.scene:
            queryset = Scene.objects.filter(game=self.get_game())

            pk = self.kwargs.get(self.game_pk_url_kwarg, None)
            queryset = queryset.filter(pk=pk)

            try:
                self.scene = queryset.get()
            except queryset.model.DoesNotExist:
                raise Http404(
                    _("No %(verbose_name)s found matching the query") %
                    {'verbose_name': queryset.model._meta.verbose_name}
                )
        return self.scene


class DetailWithSceneView(SceneMixin, DetailView):
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class DeleteWithSceneView(DetailWithSceneView, DeleteView):
    def get_success_url(self):
        scene = self.get_scene()
        return scene.get_absolute_url()

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CreateWithSceneView(SceneMixin, CreateView):
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UpdateWithSceneView(SceneMixin, UpdateView):
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class IndexView(TemplateView):
    template_name = 'index.html'
