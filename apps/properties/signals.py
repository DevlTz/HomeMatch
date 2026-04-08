from .models import Properties
from django.dispatch import receiver
from django.db.models.signals import post_delete

# É um decorator que fica "escutando" eventos que acontecem no banco
# evento = post_delete
# sender = escuta só eventos do model Properties
@receiver(post_delete, sender=Properties)
def delete_fatherless_room(sender, instance, **kwargs):
    room = getattr(instance, 'rooms', None) # instance = o propertie que foi deletado, intance.room = pega o room que o propetie usava
    if room and not room.properties.exists():  # nenhum outro imóvel usa esse room
        room.delete()
        
    extras = getattr(instance, 'rooms_extras', None) # pega os extras do imóvel deletado
    if extras and not extras.properties.exists(): # nenhum outro imóvel usa esses extras
        extras.delete()
        