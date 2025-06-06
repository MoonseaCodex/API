from rest_framework.status import *
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from codex.models.character import Character
from codex.models.items import MagicItem
from codex.models.events import ManualCreation, ManualEdit, Game
from codex.serialisers.items import MagicItemSerialiser

from codex.utils.trade import remove_adverts_for_item


class MagicItemViewSet(viewsets.GenericViewSet):
    """CRUD views for permanent magic items"""

    lookup_field = "uuid"
    lookup_url_kwarg = "uuid"
    lookup_value_regex = r"[\-0-9a-f]{36}"

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_item_source(self, request, character):
        """Get the item source from a request and sanity check it"""
        item_source_type = request.data.get("item_source_type")
        item_source = request.data.get("item_source")

        if item_source_type == "game":
            event = Game.objects.get(uuid=item_source)
            if event.characters.contains(character):
                return event
            raise ValueError("Character not associated with game")
        elif item_source_type == "level5":
            event = ManualCreation.objects.create(character=character, name="Level 5 item selection")
            return event
        elif item_source_type == "trade":
            event = ManualCreation.objects.create(character=character, name="Item trade (non-MSC)")
            return event
        elif item_source_type == "dmreward":
            event = ManualCreation.objects.create(character=character, name="Manual DM reward")
            return event

        event = ManualCreation.objects.create(character=character, name=item_source)
        return event

    def create_manualedit_event(self, existing_item, data):
        """Create a ManualEdit event to log the item update"""
        name = data.get("name")
        if name and name != existing_item.name:
            ManualEdit.objects.create(
                item=existing_item,
                character=existing_item.character,
                name="Item name changed",
                details=f"{existing_item.name} >> {name}",
            )

    def get_queryset(self):
        """Retrieve base queryset"""
        return MagicItem.objects.all()

    def create(self, request, *args, **kwargs):
        """Create a new magic item"""
        # Verify that the target character belongs to the requester
        try:
            character_uuid = request.data.get("character_uuid")
            character = Character.objects.get(uuid=character_uuid)
            if character.player != request.user:
                return Response({"message": "This character does not belong to you"}, HTTP_403_FORBIDDEN)
        except Character.DoesNotExist:
            return Response({"message": "Invalid character"}, HTTP_400_BAD_REQUEST)

        serialiser = MagicItemSerialiser(data=request.data)
        if serialiser.is_valid():
            try:
                item_source = self.get_item_source(request, character)
            except Exception as e:
                return Response({"message": "Error with item origin event"}, HTTP_400_BAD_REQUEST)
            item = serialiser.save(character=character)
            item.source = item_source
            item.save()

            new_item = MagicItemSerialiser(item)
            return Response(new_item.data, HTTP_201_CREATED)
        else:
            return Response({"message": "Item creation failed"}, HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """get a single item"""
        item = self.get_object()
        serializer = MagicItemSerialiser(item, context={"user": request.user})
        return Response(serializer.data)

    def list(self, request):
        """Retrieve a list of items for current user"""
        if request.user.is_anonymous:
            return Response({"message": "You need to log in to do that"}, HTTP_403_FORBIDDEN)

        queryset = self.get_queryset()
        character_uuid = request.query_params.get("character", None)
        if character_uuid:
            queryset = queryset.filter(character__uuid=character_uuid)
        else:
            queryset = queryset.filter(character__player=request.user)
        queryset = queryset.order_by("name")
        serialiser = MagicItemSerialiser(queryset, many=True, context={"user": request.user})
        return Response(serialiser.data, HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        """Update an existing magic item - only allow name and rarity updates"""
        existing_item = self.get_object()
        if existing_item.character.player != request.user:
            return Response({"message": "This item does not belong to you"}, HTTP_403_FORBIDDEN)

        serialiser = MagicItemSerialiser(existing_item, data=request.data, partial=True)
        if serialiser.is_valid():
            # If the item is being removed from the market
            if request.data.get("market") == False:
                remove_adverts_for_item(existing_item)

            self.create_manualedit_event(existing_item, request.data)
            item = serialiser.save()
            new_item = MagicItemSerialiser(item)
            return Response(new_item.data, HTTP_200_OK)
        else:
            return Response({"message": "Invalid data in item update"}, HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """Delete a magic item"""
        item = self.get_object()
        if item.character.player != request.user:
            return Response({"message": "This item does not belong to you"}, HTTP_403_FORBIDDEN)
        item.delete()
        return Response({"message": "Item destroyed"}, HTTP_200_OK)
