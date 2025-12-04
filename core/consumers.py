import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SeatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join the seat updates group
        self.room_group_name = 'seat_updates'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave the seat updates group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        # Handle incoming messages (optional for future features)
        pass
    
    # Receive message from room group
    async def seat_update(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'seat_update',
            'seats': event['seats']
        }))
