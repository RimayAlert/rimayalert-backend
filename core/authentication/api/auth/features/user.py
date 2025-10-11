from rest_framework.authtoken.models import Token

from core.authentication.models import User


class AuthApiUser:
    def __init__(self, request):
        self.request = request

    def __get_or_create_user(self, data):
        data_user = dict()
        data_user['dni'] = data['dni']
        data_user['first_name'] = data['first_name']
        data_user['last_name'] = data['last_name']
        data_user['email'] = data['email']
        data_user['username'] = data['username']
        user = User.get_or_create_user(data_user)
        if not user.password and data.get('password'):
            user.set_password(data['password'])
            user.save()
        return user

    def login(self, user_data):
        if not User.objects.filter(dni=user_data['dni']).exists():
            user = self.__get_or_create_user(user_data)
        else:
            user = User.objects.get(dni=user_data['dni'])

        token, _ = Token.objects.get_or_create(user=user)
        return {'user': user, 'token': token.key}


