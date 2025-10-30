from channels.generic.websocket import AsyncWebsocketConsumer
import json

class LiveConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room"]
        self.group_name = f"live_{self.room_name}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # Alles (SDP/OFFER/ANSWER/ICE) ungefiltert an alle im Raum broadcasten
        if text_data:
            await self.channel_layer.group_send(
                self.group_name,
                {"type": "signal.message", "message": text_data, "sender": self.channel_name}
            )

    async def signal_message(self, event):
        # Nicht an sich selbst zurücksenden
        if event.get("sender") == self.channel_name:
            return
        await self.send(text_data=event["message"])
