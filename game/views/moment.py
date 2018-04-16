from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from game.models import Moment
from game.views import base


class MomentDetailView(LoginRequiredMixin, base.DetailWithSceneView):
    template_name = 'game/moment/detail.html'
    model = Moment
    pk_url_kwarg = 'moment_pk'


class MomentCreateView(LoginRequiredMixin, base.CreateWithSceneView):
    template_name = 'game/moment/form.html'
    model = Moment
    fields = ['name', 'description', 'order']

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.game = self.game
        self.object.scene = self.scene
        self.object.save()
        return super().form_valid(form)


class MomentUpdateView(LoginRequiredMixin, base.UpdateWithSceneView):
    template_name = 'game/scene/form.html'
    model = Moment
    pk_url_kwarg = 'moment_pk'
    fields = ['name', 'description', 'order']


class MomentDeleteView(LoginRequiredMixin, base.DeleteWithSceneView):
    template_name = 'game/scene/delete.html'
    model = Moment
    pk_url_kwarg = 'moment_pk'
