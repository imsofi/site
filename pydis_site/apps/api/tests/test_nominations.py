from datetime import datetime as dt, timedelta, timezone

from django_hosts.resolvers import reverse

from .base import APISubdomainTestCase
from ..models import Nomination, User


class CreationTests(APISubdomainTestCase):
    @classmethod
    def setUpTestData(cls):  # noqa
        cls.user = User.objects.create(
            id=1234,
            name='joe dart',
            discriminator=1111,
            avatar_hash=None
        )

    def test_accepts_valid_data(self):
        url = reverse('bot:nomination-list', host='api')
        data = {
            'actor': self.user.id,
            'reason': 'Joe Dart on Fender Bass',
            'user': self.user.id,
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 201)

        nomination = Nomination.objects.get(id=response.json()['id'])
        self.assertAlmostEqual(
            nomination.inserted_at,
            dt.now(timezone.utc),
            delta=timedelta(seconds=2)
        )
        self.assertEqual(nomination.user.id, data['user'])
        self.assertEqual(nomination.actor.id, data['actor'])
        self.assertEqual(nomination.reason, data['reason'])
        self.assertEqual(nomination.active, True)

    def test_returns_400_on_second_active_nomination(self):
        url = reverse('bot:nomination-list', host='api')
        data = {
            'actor': self.user.id,
            'reason': 'Joe Dart on Fender Bass',
            'user': self.user.id,
        }

        response1 = self.client.post(url, data=data)
        self.assertEqual(response1.status_code, 201)

        response2 = self.client.post(url, data=data)
        self.assertEqual(response2.status_code, 400)
        self.assertEqual(response2.json(), {
            'active': ['There can only be one active nomination.']
        })

    def test_returns_400_for_missing_user(self):
        url = reverse('bot:nomination-list', host='api')
        data = {
            'actor': self.user.id,
            'reason': 'Joe Dart on Fender Bass',
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'user': ['This field is required.']
        })

    def test_returns_400_for_missing_actor(self):
        url = reverse('bot:nomination-list', host='api')
        data = {
            'user': self.user.id,
            'reason': 'Joe Dart on Fender Bass',
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'actor': ['This field is required.']
        })

    def test_returns_400_for_missing_reason(self):
        url = reverse('bot:nomination-list', host='api')
        data = {
            'user': self.user.id,
            'actor': self.user.id,
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'reason': ['This field is required.']
        })

    def test_returns_400_for_bad_user(self):
        url = reverse('bot:nomination-list', host='api')
        data = {
            'user': 1024,
            'reason': 'Joe Dart on Fender Bass',
            'actor': self.user.id,
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'user': ['Invalid pk "1024" - object does not exist.']
        })

    def test_returns_400_for_bad_actor(self):
        url = reverse('bot:nomination-list', host='api')
        data = {
            'user': self.user.id,
            'reason': 'Joe Dart on Fender Bass',
            'actor': 1024,
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'actor': ['Invalid pk "1024" - object does not exist.']
        })

    def test_returns_400_for_unnominate_reason_at_creation(self):
        url = reverse('bot:nomination-list', host='api')
        data = {
            'user': self.user.id,
            'reason': 'Joe Dart on Fender Bass',
            'actor': self.user.id,
            'unnominate_reason': "Joe Dart on the Joe Dart Bass"
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'unnominate_reason': ['This field cannot be set at creation.']
        })

    def test_returns_400_for_unwatched_at_at_creation(self):
        url = reverse('bot:nomination-list', host='api')
        data = {
            'user': self.user.id,
            'reason': 'Joe Dart on Fender Bass',
            'actor': self.user.id,
            'unwatched_at': "Joe Dart on the Joe Dart Bass"
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'unwatched_at': ['This field cannot be set at creation.']
        })

    def test_returns_400_for_inserted_at_at_creation(self):
        url = reverse('bot:nomination-list', host='api')
        data = {
            'user': self.user.id,
            'reason': 'Joe Dart on Fender Bass',
            'actor': self.user.id,
            'inserted_at': "Joe Dart on the Joe Dart Bass"
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'inserted_at': ['This field cannot be set at creation.']
        })

    def test_returns_400_for_active_at_creation(self):
        url = reverse('bot:nomination-list', host='api')
        data = {
            'user': self.user.id,
            'reason': 'Joe Dart on Fender Bass',
            'actor': self.user.id,
            'active': False
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'active': ['This field cannot be set at creation.']
        })


class NominationTests(APISubdomainTestCase):
    @classmethod
    def setUpTestData(cls):  # noqa
        cls.user = User.objects.create(
            id=1234,
            name='joe dart',
            discriminator=1111,
            avatar_hash=None
        )

        cls.active_nomination = Nomination.objects.create(
            user=cls.user,
            actor=cls.user,
            reason="He's pretty funky"
        )
        cls.inactive_nomination = Nomination.objects.create(
            user=cls.user,
            actor=cls.user,
            reason="He's pretty funky",
            active=False,
            unnominate_reason="His neck couldn't hold the funk",
            unwatched_at="5018-11-20T15:52:00+00:00"
        )

    def test_returns_200_update_reason_on_active(self):
        url = reverse('bot:nomination-detail', args=(self.active_nomination.id,), host='api')
        data = {
            'reason': "He's one funky duck"
        }

        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, 200)

        nomination = Nomination.objects.get(id=response.json()['id'])
        self.assertEqual(nomination.reason, data['reason'])

    def test_returns_400_on_frozen_field_update(self):
        url = reverse('bot:nomination-detail', args=(self.active_nomination.id,), host='api')
        data = {
            'user': "Theo Katzman"
        }

        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'user': ['This field cannot be updated.']
        })

    def test_returns_400_update_unnominate_reason_on_active(self):
        url = reverse('bot:nomination-detail', args=(self.active_nomination.id,), host='api')
        data = {
            'unnominate_reason': 'He started playing jazz'
        }

        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'unnominate_reason': ["An active nomination can't have an unnominate reason."]
        })

    def test_returns_200_update_reason_on_inactive(self):
        url = reverse('bot:nomination-detail', args=(self.inactive_nomination.id,), host='api')
        data = {
            'reason': "He's one funky duck"
        }

        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, 200)

        nomination = Nomination.objects.get(id=response.json()['id'])
        self.assertEqual(nomination.reason, data['reason'])

    def test_returns_200_update_unnominate_reason_on_inactive(self):
        url = reverse('bot:nomination-detail', args=(self.inactive_nomination.id,), host='api')
        data = {
            'unnominate_reason': 'He started playing jazz'
        }

        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, 200)

        nomination = Nomination.objects.get(id=response.json()['id'])
        self.assertEqual(nomination.unnominate_reason, data['unnominate_reason'])

    def test_returns_200_on_valid_end_nomination(self):
        url = reverse(
            'bot:nomination-end-nomination',
            args=(self.active_nomination.id,),
            host='api'
        )
        data = {
            'unnominate_reason': 'He started playing jazz'
        }
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, 200)

        nomination = Nomination.objects.get(id=response.json()['id'])

        self.assertAlmostEqual(
            nomination.unwatched_at,
            dt.now(timezone.utc),
            delta=timedelta(seconds=2)
        )
        self.assertFalse(nomination.active)
        self.assertEqual(nomination.unnominate_reason, data['unnominate_reason'])

    def test_returns_400_on_invalid_field_end_nomination(self):
        url = reverse(
            'bot:nomination-end-nomination',
            args=(self.active_nomination.id,),
            host='api'
        )
        data = {
            'reason': 'Why does a whale have feet?'
        }
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'reason': ['This field cannot be set at end_nomination.']
        })

    def test_returns_400_on_missing_unnominate_reason_end_nomination(self):
        url = reverse(
            'bot:nomination-end-nomination',
            args=(self.active_nomination.id,),
            host='api'
        )
        data = {}

        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'unnominate_reason': ['This field is required when ending a nomination.']
        })

    def test_returns_400_on_ending_inactive_nomination(self):
        url = reverse(
            'bot:nomination-end-nomination',
            args=(self.inactive_nomination.id,),
            host='api'
        )
        data = {
            'unnominate_reason': 'He started playing jazz'
        }

        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'active': ['A nomination must be active to be ended.']
        })

    def test_returns_404_on_get_unknown_nomination(self):
        url = reverse(
            'bot:nomination-detail',
            args=(9999,),
            host='api'
        )

        response = self.client.get(url, data={})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {
            "detail": "Not found."
        })

    def test_returns_404_on_patch_unknown_nomination(self):
        url = reverse(
            'bot:nomination-detail',
            args=(9999,),
            host='api'
        )

        response = self.client.patch(url, data={})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {
            "detail": "Not found."
        })

    def test_returns_404_on_end_unknown_nomination(self):
        url = reverse(
            'bot:nomination-end-nomination',
            args=(9999,),
            host='api'
        )

        data = {
            'unnominate_reason': 'He started playing jazz'
        }

        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {
            "detail": "Not found."
        })

    def test_returns_405_on_list_put(self):
        url = reverse('bot:nomination-list', host='api')

        response = self.client.put(url, data={})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json(), {
            "detail": "Method \"PUT\" not allowed."
        })

    def test_returns_405_on_list_patch(self):
        url = reverse('bot:nomination-list', host='api')

        response = self.client.patch(url, data={})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json(), {
            "detail": "Method \"PATCH\" not allowed."
        })

    def test_returns_405_on_list_delete(self):
        url = reverse('bot:nomination-list', host='api')

        response = self.client.delete(url, data={})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json(), {
            "detail": "Method \"DELETE\" not allowed."
        })

    def test_returns_405_on_detail_put(self):
        url = reverse('bot:nomination-detail', args=(self.active_nomination.id,), host='api')

        response = self.client.put(url, data={})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json(), {
            "detail": "Method \"PUT\" not allowed."
        })

    def test_returns_405_on_detail_post(self):
        url = reverse('bot:nomination-detail', args=(self.active_nomination.id,), host='api')

        response = self.client.post(url, data={})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json(), {
            "detail": "Method \"POST\" not allowed."
        })

    def test_returns_405_on_detail_delete(self):
        url = reverse('bot:nomination-detail', args=(self.active_nomination.id,), host='api')

        response = self.client.delete(url, data={})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json(), {
            "detail": "Method \"DELETE\" not allowed."
        })

    def test_returns_405_on_end_nomination_put(self):
        url = reverse(
            'bot:nomination-end-nomination',
            args=(self.inactive_nomination.id,),
            host='api'
        )

        response = self.client.put(url, data={})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json(), {
            "detail": "Method \"PUT\" not allowed."
        })

    def test_returns_405_on_end_nomination_post(self):
        url = reverse(
            'bot:nomination-end-nomination',
            args=(self.inactive_nomination.id,),
            host='api'
        )

        response = self.client.post(url, data={})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json(), {
            "detail": "Method \"POST\" not allowed."
        })

    def test_returns_405_on_end_nomination_delete(self):
        url = reverse(
            'bot:nomination-end-nomination',
            args=(self.inactive_nomination.id,),
            host='api'
        )

        response = self.client.delete(url, data={})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json(), {
            "detail": "Method \"DELETE\" not allowed."
        })

    def test_returns_405_on_end_nomination_get(self):
        url = reverse(
            'bot:nomination-end-nomination',
            args=(self.inactive_nomination.id,),
            host='api'
        )

        response = self.client.get(url, data={})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json(), {
            "detail": "Method \"GET\" not allowed."
        })
