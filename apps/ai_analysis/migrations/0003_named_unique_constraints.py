from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ai_analysis", "0002_restore_missing_subjective_tables"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=[
                        """
                        ALTER TABLE ai_analysis_photosubjectiveattribute
                        DROP CONSTRAINT IF EXISTS ai_analysis_photosubjectiveattribute_photo_id_attribute_token_0a0ba346_uniq;
                        """,
                        """
                        ALTER TABLE ai_analysis_propertysubjectiveattribute
                        DROP CONSTRAINT IF EXISTS ai_analysis_propertysubjectiveattribute_property_id_attribute_token_0ccd7f65_uniq;
                        """,
                        """
                        DROP INDEX IF EXISTS ai_analysis_photosubjectiveattribute_photo_token_uniq;
                        """,
                        """
                        DROP INDEX IF EXISTS ai_analysis_propertysubjectiveattribute_property_token_uniq;
                        """,
                        """
                        ALTER TABLE ai_analysis_photosubjectiveattribute
                        ADD CONSTRAINT ai_photo_subjective_attribute_unique_token_per_photo
                        UNIQUE (photo_id, attribute_token);
                        """,
                        """
                        ALTER TABLE ai_analysis_propertysubjectiveattribute
                        ADD CONSTRAINT ai_property_subjective_attribute_unique_token_per_property
                        UNIQUE (property_id, attribute_token);
                        """,
                    ],
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
            state_operations=[
                migrations.AlterUniqueTogether(
                    name="photosubjectiveattribute",
                    unique_together=set(),
                ),
                migrations.AlterUniqueTogether(
                    name="propertysubjectiveattribute",
                    unique_together=set(),
                ),
                migrations.AddConstraint(
                    model_name="photosubjectiveattribute",
                    constraint=models.UniqueConstraint(
                        fields=("photo", "attribute_token"),
                        name="ai_photo_subjective_attribute_unique_token_per_photo",
                    ),
                ),
                migrations.AddConstraint(
                    model_name="propertysubjectiveattribute",
                    constraint=models.UniqueConstraint(
                        fields=("property", "attribute_token"),
                        name="ai_property_subjective_attribute_unique_token_per_property",
                    ),
                ),
            ],
        ),
    ]
