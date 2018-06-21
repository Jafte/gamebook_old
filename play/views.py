from django.shortcuts import redirect
from django.urls import reverse
from game.views.game import GameDetailView


class PlayView(GameDetailView):
    template_name = 'play/detail.html'
    game_session = None

    def get_session(self):
        if not self.game_session:
            self.game_session = self.object.get_user_game(self.request.user)

        return self.game_session

    def get_context_data(self, **kwargs):
        context = {
            'session': self.get_session()
        }
        context.update(kwargs)
        return super().get_context_data(**context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        session = self.get_session()

        action = self.request.POST.get('action', False)
        if action == 'new_game':
            session.finish_game()
            return redirect(reverse('game_play', args=(self.object.pk, )))

        if action == 'do':
            action_id = self.request.POST.get('action_id', False)
            session.active_character.do_action(action_id)
            return redirect(reverse('game_play', args=(self.object.pk, )))

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
