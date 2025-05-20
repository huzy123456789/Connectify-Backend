from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Message, MessageDeliveryStatus

@receiver(post_save, sender=MessageDeliveryStatus)
def notify_message_status(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        # Notify recipient about message status
        async_to_sync(channel_layer.group_send)(
            f"user_{instance.message.sender.id}",
            {
                "type": "message.status",
                "message_id": instance.message.id,
                "status": instance.status,
                "timestamp": instance.timestamp.isoformat()
            }
        )
