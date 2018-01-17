from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from game.models import Character
from game.views.base import DeleteWithGameView, DetailWithGameView, \
                        CreateWithGameView, UpdateWithGameView


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
