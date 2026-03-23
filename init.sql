CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS rooms (
    id              BIGSERIAL PRIMARY KEY,
    bedrooms        INT,
    bathrooms       INT,
    parking_spots   INT,
    CONSTRAINT rooms_unique UNIQUE (bedrooms, bathrooms, parking_spots)
);

CREATE TABLE IF NOT EXISTS rooms_extras (
    id              BIGSERIAL PRIMARY KEY,
    living_room     BOOLEAN DEFAULT TRUE,
    garden          BOOLEAN DEFAULT FALSE,
    kitchen         BOOLEAN DEFAULT TRUE,
    laundry_room    BOOLEAN DEFAULT FALSE,
    pool            BOOLEAN DEFAULT FALSE,
    office          BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS condo (
    id              BIGSERIAL PRIMARY KEY,
    name            TEXT,
    address         TEXT, 
    gym             BOOLEAN DEFAULT FALSE,
    pool            BOOLEAN DEFAULT FALSE,
    court           BOOLEAN DEFAULT FALSE,
    parks           BOOLEAN DEFAULT FALSE,
    party_spaces    BOOLEAN DEFAULT FALSE,
    concierge       BOOLEAN DEFAULT FALSE,  
);


CREATE TABLE IF NOT EXISTS users (
    id          BIGSERIAL PRIMARY KEY,
    name        TEXT        NOT NULL,
    age         INT,
    gender      CHAR(1),
    email       TEXT        UNIQUE NOT NULL,
    created_at  TIMESTAMP   DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS properties (
    id                    BIGSERIAL PRIMARY KEY,
    owner_id              BIGINT REFERENCES users(id), 
    rooms_id              BIGINT REFERENCES rooms(id),
    rooms_extras_id       BIGINT REFERENCES rooms_extras(id),
    condo_id              BIGINT REFERENCES condo(id),
    property_purpose      CHAR(1),
    type                  CHAR(1),
    area                  FLOAT,
    floors                INT,
    floor_number          INT, 
    preco                 NUMERIC(15, 2),
    address               TEXT,
    neighborhood          TEXT,
    city                  TEXT,
    status                BOOLEAN DEFAULT TRUE,
    has_mobilia           BOOLEAN DEFAULT FALSE,
    descricao             TEXT,
    embedding             vector(1536),
    created_at            TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTIS properties_photos(
    id                  BIGSERIAL PRIMARY KEY,
    property_id         BIGINT REFERENCES properties(id),
    r2_key              TEXT NOT NULL,
    order               INT
) 