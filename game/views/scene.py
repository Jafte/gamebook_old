from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from game.models import Scene
from game.views.base import DeleteWithGameView, DetailWithGameView, CreateWithGameView, UpdateWithGameView


class SceneDetailView(LoginRequiredMixin, DetailWithGameView):
    template_name = 'game/scene/detail.html'
    model = Scene
    pk_url_kwarg = 'scene_pk'


class SceneCreateView(LoginRequiredMixin, CreateWithGameView):
    template_name = 'game/scene/form.html'
    model = Scene
    fields = ['name', 'description', 'order']

    def form_valid(self, form):
        if self.game.can_create_new_scene():
            self.object = form.save(commit=False)
            self.object.game = self.game
            self.object.save()
            return super().form_valid(form)
        else:
            return redirect(self.game.get_absolute_url())


class SceneUpdateView(LoginRequiredMixin, UpdateWithGameView):
    template_name = 'game/scene/form.html'
    model = Scene
    pk_url_kwarg = 'scene_pk'
    fields = ['name', 'description', 'order']


class SceneDeleteView(LoginRequiredMixin, DeleteWithGameView):
    template_name = 'game/scene/delete.html'
    model = Scene
    pk_url_kwarg = 'scene_pk'
