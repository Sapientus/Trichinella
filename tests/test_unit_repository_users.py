import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from src.database.models import User

from src.schemas import UserModel
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    update_avatar,
    confirmed_email,
)


class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_user_by_email(self):
        email = "test@gmail.com"
        user = MagicMock(email=email)
        self.session.query().filter().first.return_value = user
        result = await get_user_by_email(email=email, db=self.session)
        self.assertEqual(result, user)

    @patch("src.repository.users.Gravatar")
    async def test_create_user(self, MockGravatar):
        body = UserModel(
            email="test@gmail.com", username="Testname", password="test123"
        )
        mock_gravatar = MockGravatar.return_value
        mock_gravatar.get_image.return_value = "http://example.com/avatar.jpg"
        result = await create_user(body=body, db=self.session)
        self.assertEqual(result.avatar, "http://example.com/avatar.jpg")
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.password, body.password)

    @patch("src.repository.users.Gravatar")
    async def test_create_user_not_avatar(self, MockGravatar):
        body = UserModel(
            email="test@gmail.com", username="Testname", password="test123"
        )
        mock_gravatar = MockGravatar.return_value
        mock_gravatar.get_image.side_effect = Exception("Gravatar account wasn't found")
        result = await create_user(body=body, db=self.session)
        self.assertIsNone(result.avatar)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.password, body.password)

    async def test_update_avatar(self):
        email = "test@gmail.com"
        mock_user = MagicMock(email=email)
        url = "http://example.com/avatar.jpg"
        self.session.query().filter().first.return_value = mock_user
        await update_avatar(email=email, url=url, db=self.session)
        self.assertEqual(url, mock_user.avatar)
        self.session.commit.assert_called_once()

    async def test_update_token(self):
        token = "test_token"
        mock_user = MagicMock()
        self.session.query().filter().first.return_value = token
        await update_token(user=mock_user, token=token, db=self.session)
        self.assertEqual(token, mock_user.refresh_token)
        self.session.commit.assert_called_once()

    async def test_confirmed_email(self):
        email = "test@gmail.com"
        mock_user = MagicMock()
        self.session.query().filter().first.return_value = mock_user
        await confirmed_email(email=email, db=self.session)
        self.assertTrue(mock_user.confirmed)
        self.session.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
