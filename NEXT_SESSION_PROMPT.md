# 📌 PROMPT PARA IA — PRÓXIMA SESIÓN

**Copiar-pegar este texto completo en el chat con la IA**

---

```
Necesito que trabajes en el proyecto DEMAND-24 (predicción de demanda para MiniMarket).

==== CONTEXTO RÁPIDO ====
- Fase 2 (ML Engine): ✅ COMPLETADA (10 módulos, 3,469 LOC, 29 tests pasando)
- Fase 3 (Módulo de Datos): ⏳ TODO — Este es tu trabajo
- Stack: Python 3.13.5, XGBoost, Supabase, FastAPI, React

==== TAREAS PARA ENTRAR EN CONTEXTO (LEE EN ORDEN) ====

1. Lee este archivo para contexto en 30 segundos:
   → c:\Users\users\Desktop\ELÍAS\Minimarket24\QUICK_START_NEXT_SESSION.md

2. Lee las 15 decisiones arquitectónicas (15 min):
   → c:\Users\users\Desktop\ELÍAS\Minimarket24\ARCHITECTURAL_DECISIONS.md

3. Lee el roadmap detallado de Fase 3 (20 min):
   → c:\Users\users\Desktop\ELÍAS\Minimarket24\FASE3_ROADMAP.md

4. Lee la bitácora con contexto histórico SI necesitas profundizar:
   → c:\Users\users\Desktop\ELÍAS\Minimarket24\Documents\BITACORA_DESARROLLO_DEMAND24.md

==== VERIFICACIÓN RÁPIDA ====

Después de leer, verifica que todo funciona ejecutando:

```bash
cd c:\Users\users\Desktop\ELÍAS\Minimarket24
.venv\Scripts\activate
python -m pytest modulo_analitico/tests/ -v
```

Debe mostrar: **29 passed in ~3.6s** ✅

==== TU TAREA PRINCIPAL ====

Implementar **Fase 3: Módulo de Datos** siguiendo FASE3_ROADMAP.md

Tareas específicas:
1. Crear schema SQL en Supabase (4 tables)
2. Implementar SQLAlchemy models
3. Implementar Pydantic schemas
4. Implementar Repository Pattern
5. Integrar persistencia en DemandPredictor
6. Crear 20+ unit tests

**Definición de LISTO**:
- [ ] 4 tables en Supabase
- [ ] 4 SQLAlchemy models
- [ ] 4 Pydantic schemas  
- [ ] 4 Repository classes
- [ ] DemandPredictor.save_predictions_to_db() funciona
- [ ] 20+ tests nuevos PASS
- [ ] 29 tests originales SIGUEN siendo 29 PASS

==== PUNTOS CRÍTICOS ====

⚠️ NUNCA HACER:
- Hardcodear valores (TODO desde .env)
- Features ANTES del split temporal (anti-leakage)
- Cambiar CA-01 (70% SKU ≤20% MAPE)
- Silenciar excepciones

✅ HACER SIEMPRE:
- Tests para todo
- Logging en puntos críticos
- Separación de capas
- Config desde MLConfig

==== ESTRUCTURA DEL PROYECTO ====

```
modulo_analitico/          ← ML Engine (COMPLETADO ✅)
├── config/ml_config.py
├── data_adapter/
├── models/
├── training/
├── tests/                 ← 29 tests passing
└── predictor.py           ← API pública

logica_negocio/            ← Backend (TODO: Fase 3)
├── database/
│   ├── models/            ← IMPLEMENTAR
│   ├── repositories/      ← IMPLEMENTAR
│   └── schemas/           ← IMPLEMENTAR
└── config/settings.py

.env                       ← Config (ML_*, PILOT_SKU_IDS, etc.)
```

==== REFERENCIAS RÁPIDAS ====

**Configuración clave** (NO CAMBIAR):
- ML_RANDOM_SEED=42
- ML_N_SPLITS=5
- XGBOOST_MAX_DEPTH=6
- MAPE_THRESHOLD=20%
- CA-01: 70% SKU ≤20% MAPE

**API pública (DemandPredictor)**:
- load_data()
- prepare_data()
- train()
- predict()
- train_batch()
- get_evaluation_metrics()

==== SI NECESITAS AYUDA ====

- ¿Por qué hacemos X así? → Lee ARCHITECTURAL_DECISIONS.md
- ¿Cómo implemento Y? → Lee FASE3_ROADMAP.md (tiene ejemplos)
- ¿Cuál es el estado del proyecto? → Lee PROJECT_STATUS.py
- ¿Contexto histórico? → Lee BITACORA_DESARROLLO_DEMAND24.md

==== START HERE ====

1. Lee QUICK_START_NEXT_SESSION.md (5 min)
2. Lee ARCHITECTURAL_DECISIONS.md (15 min)
3. Lee FASE3_ROADMAP.md (20 min)
4. Verifica: pytest modulo_analitico/tests/ -v → 29 PASS
5. Crear rama: git checkout -b feature/fase3-modulo-datos
6. Implementar Tarea 1 de FASE3_ROADMAP.md

¿Listo? Avísame cuando termines de leer los 3 archivos.
```

---

## 📌 **VERSIÓN ULTRA-CORTA** (Si necesitas algo más breve)

```
Proyecto: DEMAND-24 (predicción de demanda)
Fase actual: 2 ✅ → 3 ⏳
Tu tarea: Implementar Fase 3 (Módulo de Datos)

LEE ESTOS 3 ARCHIVOS EN ORDEN (40 min total):
1. c:\Users\users\Desktop\ELÍAS\Minimarket24\QUICK_START_NEXT_SESSION.md
2. c:\Users\users\Desktop\ELÍAS\Minimarket24\ARCHITECTURAL_DECISIONS.md
3. c:\Users\users\Desktop\ELÍAS\Minimarket24\FASE3_ROADMAP.md

VERIFICA:
pytest modulo_analitico/tests/ -v
→ Debe mostrar: 29 passed

TAREA:
Seguir FASE3_ROADMAP.md (6 tareas concretas)

¿Contexto más profundo? Lee:
c:\Users\users\Desktop\ELÍAS\Minimarket24\Documents\BITACORA_DESARROLLO_DEMAND24.md

Listo?
```

---

## 🎯 **CUÁL USAR**

- **Prompt largo**: Si la IA entra sin contexto previo
- **Prompt corto**: Si la IA ya sabe algo del proyecto o tienes límite de tokens

Ambos tienen los mismos archivos en el mismo orden.
