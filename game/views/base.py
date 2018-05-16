from django.http import Http404
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.base import ContextMixin
from game.models import Game, Scene, Moment


class IndexView(TemplateView):
    template_name = 'index.html'


class GameMixin(ContextMixin):
    game_pk_url_kwarg = 'game_pk'
    game = None

    def dispatch(self, request, *args, **kwargs):
        self.game = self.get_game()
        return super().dispatch(request, *args, **kwargs)

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
    pass


class DeleteWithGameView(DetailWithGameView, DeleteView):
    def get_success_url(self):
        return self.game.get_absolute_url()


class CreateWithGameView(GameMixin, CreateView):
    pass


class UpdateWithGameView(GameMixin, UpdateView):
    pass


class SceneMixin(GameMixin):
    scene_pk_url_kwarg = 'scene_pk'
    scene = None

    def dispatch(self, request, *args, **kwargs):
        self.scene = self.get_scene()
        return super().dispatch(request, *args, **kwargs)

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
    pass


class DeleteWithSceneView(DetailWithSceneView, DeleteView):
    def get_success_url(self):
        return self.scene.get_absolute_url()


class CreateWithSceneView(SceneMixin, CreateView):
    pass


class UpdateWithSceneView(SceneMixin, UpdateView):
    pass


class MomentMixin(SceneMixin):
    moment_pk_url_kwarg = 'moment_pk'
    moment = None

    def dispatch(self, request, *args, **kwargs):
        self.moment = self.get_moment()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {
            'moment': self.get_moment()
        }
        context.update(kwargs)
        return super().get_context_data(**context)

    def get_moment(self):
        if not self.moment:
            queryset = Moment.objects.filter(game=self.get_game(), scene=self.get_scene())

            pk = self.kwargs.get(self.moment_pk_url_kwarg, None)
            queryset = queryset.filter(pk=pk)

            try:
                self.block = queryset.get()
            except queryset.model.DoesNotExist:
                raise Http404(
                    _("No %(verbose_name)s found matching the query") %
                    {'verbose_name': queryset.model._meta.verbose_name}
                )
        return self.block


class DetailWithMomentView(MomentMixin, DetailView):
    pass


class DeleteWithMomentView(DetailWithMomentView, DeleteView):
    def get_success_url(self):
        return self.moment.get_absolute_url()


class CreateWithMomentView(MomentMixin, CreateView):
    pass


class UpdateWithMomentView(MomentMixin, UpdateView):
    pass
