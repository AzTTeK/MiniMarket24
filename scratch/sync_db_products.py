from logica_negocio.config.settings import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from logica_negocio.database.models.base import Base
from logica_negocio.database.models.sku import Sku
import os

products = [
    {'product': 'Leche entera 1L', 'code': 'DAIRY-1'},
    {'product': 'Agua 500ml', 'code': 'BEVERAGES-1'},
    {'product': 'Pan tajado 500g', 'code': 'BREAD-1'},
    {'product': 'Huevos x30', 'code': 'EGGS-1'},
    {'product': 'Jabon liquido 1L', 'code': 'CLEAN-1'},
    {'product': 'Arroz 1kg', 'code': 'GROCERY-1'},
    {'product': 'Yogurt natural 200g', 'code': 'DAIRY-2'},
    {'product': 'Detergente 500ml', 'code': 'HOME-1'},
    {'product': 'Shampoo 400ml', 'code': 'PERSONAL-1'},
    {'product': 'Tomates 1kg', 'code': 'PRODUCE-1'},
    {'product': 'Carne molida 500g', 'code': 'MEATS-1'},
    {'product': 'Aceite vegetal 1L', 'code': 'GROCERY-2'},
    {'product': 'Galletas surtidas', 'code': 'SNACKS-1'},
    {'product': 'Queso crema 250g', 'code': 'DAIRY-3'},
    {'product': 'Papel higienico x4', 'code': 'HOME-2'},
    {'product': 'Pasta 500g', 'code': 'GROCERY-3'},
    {'product': 'Cafe 250g', 'code': 'GROCERY-4'},
    {'product': 'Azucar 1kg', 'code': 'GROCERY-5'},
    {'product': 'Sal 1kg', 'code': 'GROCERY-6'},
    {'product': 'Atun en lata', 'code': 'GROCERY-7'},
    {'product': 'Mayonesa 200g', 'code': 'GROCERY-8'},
    {'product': 'Salsa de tomate 200g', 'code': 'GROCERY-9'},
    {'product': 'Detergente liquido 1L', 'code': 'HOME-3'},
    {'product': 'Jabon de tocador', 'code': 'PERSONAL-2'},
    {'product': 'Desodorante', 'code': 'PERSONAL-3'},
    {'product': 'Cereal de maiz 500g', 'code': 'GROCERY-10'},
    {'product': 'Mermelada de fresa', 'code': 'GROCERY-11'},
    {'product': 'Atun en aceite', 'code': 'GROCERY-12'},
    {'product': 'Lentejas 500g', 'code': 'GROCERY-13'},
    {'product': 'Frijoles 500g', 'code': 'GROCERY-14'},
]

def sync_db():
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        count = 0
        for p in products:
            exists = db.query(Sku).filter(Sku.sku_code == p['code']).first()
            if not exists:
                new_sku = Sku(sku_code=p['code'], description=p['product'])
                db.add(new_sku)
                count += 1
        db.commit()
        print(f"Sincronizacion completada: {count} productos nuevos agregados a la base de datos.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    sync_db()
