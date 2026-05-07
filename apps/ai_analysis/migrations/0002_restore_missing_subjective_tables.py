from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("ai_analysis", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                """
                CREATE TABLE IF NOT EXISTS ai_analysis_photosubjectiveattribute (
                    id BIGSERIAL PRIMARY KEY,
                    attribute_token VARCHAR(100) NOT NULL,
                    strength DOUBLE PRECISION NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    property_id BIGINT NOT NULL
                        REFERENCES properties_properties (id)
                        DEFERRABLE INITIALLY DEFERRED,
                    photo_id BIGINT NOT NULL
                        REFERENCES properties_propertiesphotos (id)
                        DEFERRABLE INITIALLY DEFERRED
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS ai_analysis_propertysubjectiveattribute (
                    id BIGSERIAL PRIMARY KEY,
                    attribute_token VARCHAR(100) NOT NULL,
                    strength_mean DOUBLE PRECISION NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    property_id BIGINT NOT NULL
                        REFERENCES properties_properties (id)
                        DEFERRABLE INITIALLY DEFERRED
                );
                """,
                """
                CREATE INDEX IF NOT EXISTS ai_analysis_photosubjectiveattribute_property_id_idx
                    ON ai_analysis_photosubjectiveattribute (property_id);
                """,
                """
                CREATE INDEX IF NOT EXISTS ai_analysis_photosubjectiveattribute_photo_id_idx
                    ON ai_analysis_photosubjectiveattribute (photo_id);
                """,
                """
                CREATE INDEX IF NOT EXISTS ai_analysis_propertysubjectiveattribute_property_id_idx
                    ON ai_analysis_propertysubjectiveattribute (property_id);
                """,
                """
                CREATE UNIQUE INDEX IF NOT EXISTS ai_analysis_photosubjectiveattribute_photo_token_uniq
                    ON ai_analysis_photosubjectiveattribute (photo_id, attribute_token);
                """,
                """
                CREATE UNIQUE INDEX IF NOT EXISTS ai_analysis_propertysubjectiveattribute_property_token_uniq
                    ON ai_analysis_propertysubjectiveattribute (property_id, attribute_token);
                """,
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
