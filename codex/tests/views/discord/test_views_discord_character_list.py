from rest_framework.status import *
from django.urls import reverse

from codex.models.api_keys import APIKey
from codex.models.users import CodexUser


from codex.tests.views.discord.discord_test_base import DiscordBaseTest


class TestDiscordBotCharacterSearch(DiscordBaseTest):
    """Tests for DiscordBot API functionality"""

    fixtures = ["test_users", "test_characters", "test_apikeys"]

    def test_search_by_valid_discord_id(self) -> None:
        """Check that a discord ID for a player brings back their public characters"""
        apikey = APIKey.objects.get(pk=1)
        user = CodexUser.objects.get(username="testuser1")

        test_data = {"apikey": apikey.value, "discord_id": user.discord_id.lower()}
        response = self.client.post(reverse("discord_characters_list"), test_data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 2)
        self.assertIn("name", response.data[0])
        self.assertEqual("Meepo", response.data[0]["name"])

    def test_search_by_invalid_discord_id(self) -> None:
        """Check that a discord ID for a player brings back their public characters"""
        apikey = APIKey.objects.get(pk=1)
        user = CodexUser.objects.get(username="testuser1")

        test_data = {"apikey": apikey.value, "discord_id": "DrizztGod#0001"}
        response = self.client.post(reverse("discord_characters_list"), test_data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 0)

    def test_search_by_discord_id_with_space(self) -> None:
        """Check that a discord ID for a player brings back their public characters"""
        apikey = APIKey.objects.get(pk=1)
        user = CodexUser.objects.get(username="testuser1")
        user.discord_id = "Volothamp Gedarm#1337"
        user.save()

        test_data = {"apikey": apikey.value, "discord_id": user.discord_id}
        response = self.client.post(reverse("discord_characters_list"), test_data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 2)
        self.assertIn("name", response.data[0])
        self.assertEqual("Meepo", response.data[0]["name"])
