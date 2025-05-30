import uuid
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.functions import Upper


from .character import Character


class Rarities(models.TextChoices):
    """Item classifications"""

    COMMON = "common", ("Common")
    UNCOMMON = "uncommon", ("Uncommon")
    RARE = "rare", ("Rare")
    VERYRARE = "veryrare", ("Very Rare")
    LEGENDARY = "legendary", ("Legendary")


class ConsumableTypes(models.TextChoices):
    """Types of consumable items"""

    SCROLL = "scroll", ("Spell scroll")
    POTION = "potion", ("Potion")
    AMMO = "ammo", ("Ammunition")
    GEAR = "gear", ("Adventuring Gear")
    OTHER = "other", ("Other item")


class Consumable(models.Model):
    """Describes a consumable item such as a potion or a scroll"""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=256, help_text="Item Name")
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name="consumables")
    type = models.TextField(choices=ConsumableTypes.choices, default=ConsumableTypes.SCROLL, help_text="Item type")
    equipped = models.BooleanField(default=False, help_text="Item is currently equipped by its owner")
    charges = models.IntegerField(null=True, blank=True, help_text="Number of charges")
    rarity = models.CharField(
        choices=Rarities.choices, max_length=16, default=Rarities.UNCOMMON, help_text="Item rarity"
    )
    description = models.TextField(blank=True, null=True)

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name="Origin Type",
        null=True,
        help_text="Type of event that resulted in this object coming to you",
    )
    object_id = models.PositiveIntegerField(
        verbose_name="Event ID", null=True, help_text="ID of the specific source event"
    )
    source = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        """String representation"""
        if self.charges:
            return f"{self.name} [{self.charges}]"
        return f"{self.name}"


class MagicItem(models.Model):
    """A record of a permanant magical item"""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=256, help_text="Base item name")
    description = models.TextField(blank=True, null=True)
    flavour = models.TextField(help_text="Flavour text", null=True, blank=True)
    rp_name = models.TextField(help_text="Roleplay name", null=True, blank=True)
    minor_properties = models.TextField(help_text="Minor properties - guardian, etc", null=True, blank=True)
    url = models.URLField(help_text="Link to item details", null=True, blank=True)
    rarity = models.CharField(
        choices=Rarities.choices, max_length=16, default=Rarities.UNCOMMON, help_text="Item rarity"
    )
    attunement = models.BooleanField(default=False, help_text="Item requires attunement to be used")

    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name="magicitems")
    equipped = models.BooleanField(default=False, help_text="Item is currently equipped by its owner")
    market = models.BooleanField(default=False, help_text="Item is in trading post")
    # source information (game / shopping / dm service reward / trade)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name="Origin Type",
        null=True,
        help_text="Type of event that resulted in this object coming to you",
    )
    object_id = models.PositiveIntegerField(
        verbose_name="Event ID", null=True, help_text="ID of the specific source event"
    )
    source = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        """String representation"""
        if self.rp_name:
            return f"{self.rp_name} ({self.rarity})"
        return f"{self.name} ({self.rarity})"

    class Meta:
        indexes = [
            models.Index(fields=["uuid"], name="item_uuid_idx"),
            models.Index(fields=["character"], name="item_character_idx"),
            models.Index(fields=["name"], name="item_name_idx"),
            models.Index(fields=["rp_name"], name="item_rp_name_idx"),
            models.Index(Upper("name"), name="item_name_upper_idx"),
            models.Index(Upper("rp_name"), name="item_rp_name_upper_idx"),
            models.Index(fields=["market"], name="item_tradable_idx"),
            models.Index(fields=["content_type", "object_id"], name="item_source_idx"),
        ]
