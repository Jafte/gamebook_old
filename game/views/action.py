from django.contrib.auth.mixins import LoginRequiredMixin
from game.models import Action
from game.views import base


class ActionDetailView(LoginRequiredMixin, base.DetailWithMomentView):
    template_name = 'game/action/detail.html'
    model = Action
    pk_url_kwarg = 'action_pk'


class ActionCreateView(LoginRequiredMixin, base.CreateWithMomentView):
    template_name = 'game/action/form.html'
    model = Action
    fields = ['content', 'condition', 'order']

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.game = self.game
        self.object.scene = self.scene
        self.object.block = self.block
        self.object.moment = self.moment
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return self.moment.get_absolute_url()


class ActionUpdateView(LoginRequiredMixin, base.UpdateWithMomentView):
    template_name = 'game/action/form.html'
    model = Action
    pk_url_kwarg = 'action_pk'
    fields = ['content', 'condition', 'order']

    def get_success_url(self):
        return self.moment.get_absolute_url()


class ActionDeleteView(LoginRequiredMixin, base.DeleteWithMomentView):
    template_name = 'game/action/delete.html'
    model = Action
    pk_url_kwarg = 'action_pk'

    def get_success_url(self):
        return self.moment.get_absolute_url()
