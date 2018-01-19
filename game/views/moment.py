from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from game.models import Moment
from game.views.base import DeleteWithGameView, DetailWithGameView, \
                        CreateWithGameView, UpdateWithGameView


class MomentDetailView(LoginRequiredMixin, DetailWithGameView):
    template_name = 'game/moment/detail.html'
    model = Moment
    pk_url_kwarg = 'moment_pk'


class MomentCreateView(LoginRequiredMixin, CreateWithGameView):
    template_name = 'game/moment/form.html'
    model = Moment
    fields = ['name', 'description', 'order']

    def form_valid(self, form):
        if self.game.can_create_new_scene():
            self.object = form.save(commit=False)
            self.object.game = self.game
            self.object.save()
            return super().form_valid(form)
        else:
            return redirect(self.game.get_absolute_url())


class MomentUpdateView(LoginRequiredMixin, UpdateWithGameView):
    template_name = 'game/scene/form.html'
    model = Moment
    pk_url_kwarg = 'moment_pk'
    fields = ['name', 'description', 'order']


class MomentDeleteView(LoginRequiredMixin, DeleteWithGameView):
    template_name = 'game/scene/delete.html'
    model = Moment
    pk_url_kwarg = 'moment_pk'
