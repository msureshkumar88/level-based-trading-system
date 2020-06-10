class Authentication:
    def __init__(self, request):
        self.request = request
        self.user_session = "user_session"

    def save_user_session(self, value):
         self.request.session[self.user_session] = value

    def get_user_session(self):
        return self.request.session[self.user_session]

    def is_user_logged_in(self):
        if self.user_session in self.request.session.keys():
            return True
        return False

    def logout(self):
        del self.request.session[self.user_session]


