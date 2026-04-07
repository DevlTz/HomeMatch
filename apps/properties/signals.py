from .models import Properties
from django.dispatch import receiver
from django.db.models.signals import post_delete

# É um decorator que fica "escutando" eventos que acontecem no banco
# evento = post_delete
# sender = escuta só eventos do model Properties
@receiver(post_delete, sender=Properties)
def delete_fatherless_room(sender, instance, **kwargs):
    room = instance.rooms # instance = o propertie que foi deletado, intance.room = pega o room que o propetie usava
    if not room.properties.exists():  # nenhum outro imóvel usa esse room
        room.delete()