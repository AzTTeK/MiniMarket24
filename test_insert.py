import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from modulo_analitico.predictor import DemandPredictor

engine = create_engine('sqlite:///./demand24_demo.db')
Session = sessionmaker(bind=engine)
db = Session()

df = pd.DataFrame({
    'week_start': [pd.Timestamp('2026-05-18')],
    'sku_id': [1],
    'predicted_demand': [100.0],
    'confidence_level': [0.9],
    'lower_bound': [90.0],
    'upper_bound': [110.0],
    'mape': [20.0]
})

p = DemandPredictor()
try:
    p.save_predictions_to_db(df, db)
    db.commit()
    print('Exito insercion!')
except Exception as e:
    import traceback
    print(f'Error capturado: {e}')
    traceback.print_exc()
