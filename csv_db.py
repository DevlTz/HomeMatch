import pandas as pd 
import psycopg2


df = pd.read_csv('VivaRealData.csv')
df["Cidade"] = df["Bairro"].apply(lambda x: x.split(",")[-1].strip())


db_ip = 'localhost'
db_port = '9432'
db_name = 'homematch'
db_user = 'admin'
db_password = '123456'

def colect_data():
    clean = df.dropna(subset=["Endereço", "Área(m²)"]).copy()

    clean["Área(m²)"] = clean["Área(m²)"].str.replace(" m²", "", regex=False).str.strip()
    clean["Área(m²)"] = pd.to_numeric(clean["Área(m²)"], errors="coerce")
    
    clean["Área(m²)"]  = clean["Área(m²)"].astype(float)
    clean["Quartos"]   = pd.to_numeric(clean["Quartos"],   errors="coerce").astype("Int64")
    clean["Banheiros"] = pd.to_numeric(clean["Banheiros"], errors="coerce").astype("Int64")
    clean["Vagas"]     = pd.to_numeric(clean["Vagas"],     errors="coerce").astype("Int64")
    clean["Preço(R$)"] = pd.to_numeric(clean["Preço(R$)"], errors="coerce")

        
        
    clean = clean.rename(columns={
        "Endereço"  : "{#ADDRESS}",
        "Bairro"    : "{#NEIGHBORHOOD}",
        "Cidade"    : "{#CITY}",
        "Área(m²)"  : "{#AREA}",
        "Quartos"   : "{#BEDROOMS}",
        "Banheiros" : "{#BATHROOMS}",
        "Vagas"     : "{#PARKING_SPOTS}",
        "Preço(R$)" : "{#PRICE}",
    })

    return [
        {k: (None if pd.isna(v) else v) for k, v in row.items()}
        for row in clean.to_dict(orient="records")
    ]

def get_or_create_rooms( bedrooms, bathrooms, parking_spots, cur):
    print(f"rooms -> bedrooms={bedrooms}, bathrooms={bathrooms}, parking_spots={parking_spots}")
    cur.execute("""
    INSERT INTO rooms (bedrooms, bathrooms, parking_spots)
    VALUES (%s, %s, %s)
    ON CONFLICT (bedrooms, bathrooms, parking_spots) DO NOTHING
    """, (bedrooms, bathrooms, parking_spots))

    cur.execute("""
        SELECT id FROM rooms
        WHERE bedrooms IS NOT DISTINCT FROM %s
          AND bathrooms IS NOT DISTINCT FROM %s
          AND parking_spots IS NOT DISTINCT FROM %s
    """, (bedrooms, bathrooms, parking_spots))
    return cur.fetchone()[0]

def create_rooms_extras(cur):
    print("aqui 3")
    cur.execute("""
        INSERT INTO rooms_extras DEFAULT VALUES
        RETURNING id
    """)
    row = cur.fetchone()
    return row[0] if row else None

def send_database(colected_data):
    try:
            conn = psycopg2.connect(
                host=db_ip,
                port=db_port,
                user=db_user,
                password=db_password,
                dbname=db_name
            )
            cur = conn.cursor()
            print("Conectado ao PostgreSQL com sucesso.")
    except Exception as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        return


    try:
        print("aqui 1")
        for c in colected_data:
            rooms_id = get_or_create_rooms(
                c.get("{#BEDROOMS}"),
                c.get("{#BATHROOMS}"),
                c.get("{#PARKING_SPOTS}"),
                cur
            )


            cur.execute("""
                INSERT INTO properties (address, neighborhood, city, area, preco, rooms_id, rooms_extras_id, property_purpose, type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                c.get("{#ADDRESS}"),
                c.get("{#NEIGHBORHOOD}"),
                c.get("{#CITY}"),
                c.get("{#AREA}"),
                c.get("{#PRICE}"),
                rooms_id,
                1,
                'S',
                'A'
            ))

        conn.commit()
        print(f"{len(colected_data)} registros inseridos com sucesso!")
    except Exception as e:
        print(f"Erro durante UPSERT em v: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    colected_data = colect_data()
    send_database(colected_data)