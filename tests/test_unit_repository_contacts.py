import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel, ContactUpdate
from src.repository.contacts import (
    get_contacts,
    get_contact,
    create_contact,
    remove_contact,
    update_contact,
    get_birthdays,
    get_search_contacts,
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_contacts(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactModel(
            firstname="testname",
            lastname="testlastname",
            email="test@gmail.com",
            phone=1234567890,
            birthday="2000-10-12",
        )
        result = await create_contact(body=body, user=self.user, db=self.session)
        self.assertEqual(result.firstname, body.firstname)
        self.assertEqual(result.lastname, body.lastname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birthday, body.birthday)
        self.assertEqual(result.user, self.user)
        self.assertTrue(hasattr(result, "id"))

    async def test_remove_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_contact_found(self):
        body = ContactUpdate(
            firstname="testname",
            lastname="testlastname",
            email="test@gmail.com",
            phone=1234567890,
            birthday="2000-10-12",
            done=True,
        )
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact(
            contact_id=1, body=body, user=self.user, db=self.session
        )
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        body = ContactUpdate(
            firstname="testname",
            lastname="testlastname",
            email="test@gmail.com",
            phone=1234567890,
            birthday="2000-12-10",
            done=True,
        )
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact(
            contact_id=1, body=body, user=self.user, db=self.session
        )
        self.assertIsNone(result)

    async def test_get_search_contacts(self):
        search_word = "test"
        contact = ContactModel(
            firstname="test",
            lastname="lastname",
            email="test@gmail.com",
            phone=1234567890,
            birthday="2000-10-12",
            user=self.user,
        )
        self.session.query().filter().first.return_value = contact
        result = await get_search_contacts(
            search_word=search_word, user=self.user, db=self.session
        )
        self.assertEqual(result, contact)

    @patch("datetime.datetime")
    @patch("datetime.timedelta")
    async def test_get_birthdays(self, mock_datetime, mock_timedelta):
        mock_birth = mock_datetime.now().date()
        mock_delta = mock_timedelta(days=7)
        birth = mock_delta + mock_birth
        contacts = [
            Contact(birthday=birth),
            Contact(birthday=birth),
            Contact(birthday=birth),
        ]
        self.session.query().filter().all.return_value = contacts
        result = await get_birthdays(user=self.user, db=self.session)
        self.assertEqual(result, contacts)


if __name__ == "__main__":
    unittest.main()
