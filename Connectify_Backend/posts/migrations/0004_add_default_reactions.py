from django.db import migrations

def create_default_reactions(apps, schema_editor):
    ReactionType = apps.get_model('posts', 'ReactionType')
    default_reactions = [
        {'name': 'LIKE', 'emoji': '👍'},
        {'name': 'LOVE', 'emoji': '❤️'},
        {'name': 'HAHA', 'emoji': '😂'},
        {'name': 'WOW', 'emoji': '😮'},
        {'name': 'SAD', 'emoji': '😢'},
        {'name': 'ANGRY', 'emoji': '😠'},
    ]
    
    for reaction in default_reactions:
        ReactionType.objects.get_or_create(
            name=reaction['name'],
            emoji=reaction['emoji']
        )

def remove_default_reactions(apps, schema_editor):
    ReactionType = apps.get_model('posts', 'ReactionType')
    ReactionType.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('posts', '0003_trend'),
    ]

    operations = [
        migrations.RunPython(create_default_reactions, remove_default_reactions),
    ]
