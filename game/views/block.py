from django.contrib.auth.mixins import LoginRequiredMixin
from game.models import Block
from game.views import base


class BlockDetailView(LoginRequiredMixin, base.DetailWithMomentView):
    template_name = 'game/block/detail.html'
    model = Block
    pk_url_kwarg = 'block_pk'


class BlockCreateView(LoginRequiredMixin, base.CreateWithMomentView):
    template_name = 'game/block/form.html'
    model = Block
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


class BlockUpdateView(LoginRequiredMixin, base.UpdateWithMomentView):
    template_name = 'game/block/form.html'
    model = Block
    pk_url_kwarg = 'block_pk'
    fields = ['content', 'condition', 'order']

    def get_success_url(self):
        return self.moment.get_absolute_url()


class BlockDeleteView(LoginRequiredMixin, base.DeleteWithMomentView):
    template_name = 'game/block/delete.html'
    model = Block
    pk_url_kwarg = 'block_pk'

    def get_success_url(self):
        return self.moment.get_absolute_url()
