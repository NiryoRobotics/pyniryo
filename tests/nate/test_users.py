from datetime import timedelta, datetime
from uuid import uuid4

from pyniryo.nate import models
from pyniryo.nate._internal import transport_models, paths_gen
from pyniryo.nate.components.users import Users

from .base import BaseTestComponent

base_user = models.User(
    id=str(uuid4()),
    name='Marneus Calgar',
    email='marneus.calgar@ultramar.terra',
    role=models.Role(id=0, name='Chapter Master'),
)
user_endpoint = paths_gen.Users.USER.format(user_id=base_user.id)

base_token = models.Token(
    id=uuid4(),
    token='token',
    expires_at=datetime.now() + timedelta(1),
    created_at=datetime.now(),
)


class TestUsers(BaseTestComponent):

    def setUp(self):
        super().setUp()
        self.users = Users(http_client=self.http_client, mqtt_client=self.mqtt_client)

    def tearDown(self):
        del self.users

    def test_get_all(self):
        t_models = transport_models.UserList([base_user.to_transport_model()])
        self.http_client.get.return_value = t_models

        users = self.users.get_all()
        self.http_client.get.assert_called_once_with(paths_gen.Users.USERS, transport_models.UserList)
        self.assertEqual(users, [models.User.from_transport_model(u) for u in t_models.root])

    def test_create(self):
        self.http_client.post.return_value = base_user.to_transport_model()
        user = self.users.create(base_user.email, base_user.name, base_user.role.id, 'password')
        self.http_client.post.assert_called_once()
        self.assertEqual(user, base_user)

    def test_get(self):
        self.http_client.get.return_value = base_user.to_transport_model()
        user = self.users.get(base_user.id)
        self.http_client.get.assert_called_once_with(user_endpoint, transport_models.User)
        self.assertEqual(user, base_user)

    def test_delete(self):
        self.http_client.delete.return_value = None
        self.users.delete(base_user.id)
        self.http_client.delete.assert_called_once_with(user_endpoint)

    def test_update(self):
        self.http_client.patch.return_value = base_user.to_transport_model()
        user = self.users.update(base_user)
        self.http_client.patch.assert_called_once_with(user_endpoint,
                                                       base_user.to_transport_model(),
                                                       transport_models.User)
        self.assertEqual(user, base_user)

    def test_get_tokens(self):
        t_models = transport_models.TokenList([base_token.to_transport_model()])
        self.http_client.get.return_value = t_models
        tokens = self.users.get_tokens(base_user.id)
        self.http_client.get.assert_called_once_with(paths_gen.Users.USER_TOKENS.format(user_id=base_user.id),
                                                     transport_models.TokenList)
        self.assertEqual(tokens, [models.Token.from_transport_model(t) for t in t_models.root])

    def test_create_token(self):
        self.http_client.post.return_value = base_token.to_transport_model()
        token = self.users.create_token(base_user.id, datetime.now() + timedelta(1))
        self.http_client.post.assert_called_once()
        self.assertEqual(token, base_token)

    def test_update_password(self):
        self.http_client.patch.return_value = None
        self.users.update_password(base_user.id, 'password', 'new_password')

        self.assertIsNone(
            self.http_client.patch.assert_called_once_with(
                paths_gen.Users.USER_PASSWORD.format(user_id=base_user.id),
                transport_models.UpdatePassword(old_password='password', new_password='new_password'),
                None,
            ))
