# Comparativa de Etapas - Referencia Rápida

## 📊 Tabla Comparativa

| Aspecto | ETAPA 1: Prototipado | ETAPA 2: Estructuración | ETAPA 3: Escalado |
|---------|---------------------|------------------------|-------------------|
| **Duración típica** | 1-3 días | 4-10 días | 2+ semanas |
| **Objetivo** | Probar idea | Hacer mantenible | Preparar crecimiento |
| **Prioridad** | Velocidad | Balance | Robustez |
| **Archivos típicos** | 1-3 | 5-7 | 10+ |
| **Complejidad** | Mínima | Justificada | Necesaria |
| **Abstracciones** | ❌ Cero | ⚠️ Solo con dolor real | ✅ Planificadas |
| **Clases vs Funciones** | Funciones | Mix justificado | Lo que necesites |
| **Configuración** | ❌ Hardcoded | ⚠️ Básica si necesario | ✅ Completa |
| **Tests** | test_full_flow.sh | test_full_flow.sh + básicos | Cobertura completa |
| **Documentación** | README básico | Inline comments | Docs completos |
| **Patterns permitidos** | ❌ Ninguno | ⚠️ Pocos (Adapter, Strategy) | ✅ Los que necesites |

---

## 🎯 Criterios de Transición

### ¿Cuándo pasar de Etapa 1 → 2?

| Criterio | ¿Se cumple? |
|----------|-------------|
| Has usado el prototipo 3+ veces | [ ] |
| Sabes qué partes duelen | [ ] |
| Tienes 2+ casos de uso reales | [ ] |
| El código se vuelve difícil de modificar | [ ] |
| Hay duplicación clara | [ ] |

**Si 3+ checkmarks → Adelante a Etapa 2**

### ¿Cuándo pasar de Etapa 2 → 3?

| Criterio | ¿Se cumple? |
|----------|-------------|
| Código en producción/uso real | [ ] |
| 2+ usuarios diferentes | [ ] |
| Necesitas extensibilidad probada | [ ] |
| Aparecen patrones claros de evolución | [ ] |
| El sistema tiene 2+ subsistemas complejos | [ ] |

**Si 3+ checkmarks → Adelante a Etapa 3**

---

## 🚦 Señales de Alerta

### 🔴 Demasiado Simple (Under-Engineering)

| Señal | Etapa 1 | Etapa 2 | Etapa 3 |
|-------|---------|---------|---------|
| Código duplicado 3+ veces | ⚠️ OK por ahora | 🔴 Problema | 🔴 Problema serio |
| Función 100+ líneas | ⚠️ OK por ahora | 🔴 Problema | 🔴 Problema serio |
| Cambio requiere 5+ archivos | ⚠️ OK (pocos archivos) | 🔴 Problema | 🔴 Problema serio |
| Sin boundaries claros | ✅ Esperado | ⚠️ Revisar | 🔴 Problema |
| Tests frágiles | ✅ Normal | ⚠️ Preocupante | 🔴 Bloqueante |

### 🔴 Demasiado Complejo (Over-Engineering)

| Señal | Etapa 1 | Etapa 2 | Etapa 3 |
|-------|---------|---------|---------|
| Abstracciones sin 2+ impls | 🔴 Eliminar | 🔴 Eliminar | ⚠️ Justificar |
| Patterns sin dolor claro | 🔴 Eliminar | 🔴 Eliminar | ⚠️ Revisar |
| 3+ layers entre input/output | 🔴 Simplificar | ⚠️ Justificar | ✅ Puede ser OK |
| Config para todo | 🔴 Eliminar | ⚠️ Reducir | ✅ Apropiado |
| Factories con 1 tipo | 🔴 Eliminar | 🔴 Eliminar | ⚠️ Justificar |

---

## ✅ Sweet Spot por Etapa

### Etapa 1 - Características ideales:
- ✅ 1-2 archivos Python
- ✅ Funciones descriptivas
- ✅ Hardcoded pero funcional
- ✅ test_full_flow.sh pasa
- ✅ Ejecuta en <5 minutos
- ✅ Un junior entiende el código

### Etapa 2 - Características ideales:
- ✅ 5-7 archivos organizados
- ✅ Responsabilidades claras
- ✅ Sin duplicación
- ✅ Cambios localizados
- ✅ Tests no frágiles
- ✅ Patterns solo si justificados
- ✅ Un junior puede añadir features

### Etapa 3 - Características ideales:
- ✅ Arquitectura documentada
- ✅ Extensibilidad clara
- ✅ Multiple implementations
- ✅ Tests comprehensivos
- ✅ Performance considerado
- ✅ Múltiples equipos pueden contribuir

---

## 🛠️ Herramientas por Etapa

### Etapa 1
```bash
# Solo necesitas:
- Editor de texto
- Python/tu lenguaje
- test_full_flow.sh
- Claude Code
```

### Etapa 2
```bash
# Añades:
- Linter (pylint, flake8)
- Formatter (black, prettier)
- Type checker (mypy, TypeScript)
- Estructura de carpetas básica
```

### Etapa 3
```bash
# Añades:
- CI/CD pipeline
- Coverage tools
- Documentation generator
- Profiler
- Monitoring
```

---

## 📝 Templates de Decisión

### "¿Necesito una clase?"

| Contexto | Etapa 1 | Etapa 2 | Etapa 3 |
|----------|---------|---------|---------|
| Función con 2-3 params | 🟢 Función | 🟢 Función | 🟢 Función |
| Función con 5+ params | 🟡 Función con dict | 🟡 Función o clase | 🟢 Clase |
| Estado mutable compartido | 🔴 Evitar | 🟢 Clase | 🟢 Clase |
| Múltiples operaciones en mismo estado | 🔴 Evitar | 🟢 Clase | 🟢 Clase |

### "¿Necesito un módulo nuevo?"

| Criterio | Etapa 1 | Etapa 2 | Etapa 3 |
|----------|---------|---------|---------|
| Archivo tiene 100+ líneas | 🟡 Tolerable | 🟡 Considerar split | 🟢 Split |
| Archivo tiene 200+ líneas | 🔴 Split ahora | 🔴 Split ahora | 🔴 Split ahora |
| Responsabilidad clara y separada | 🟡 Mantener junto | 🟢 Separar | 🟢 Separar |
| Usado en 1 solo lugar | 🟢 Inline | 🟢 Inline | 🟡 Puede separar |

### "¿Necesito un pattern?"

| Pattern | Etapa 1 | Etapa 2 | Etapa 3 |
|---------|---------|---------|---------|
| Factory | 🔴 Nunca | 🟡 Si 3+ tipos | 🟢 Si justificado |
| Strategy | 🔴 Nunca | 🟢 Si 3+ algoritmos | 🟢 Si justificado |
| Observer | 🔴 Nunca | 🟡 Si eventos reales | 🟢 Si justificado |
| Adapter | 🔴 Nunca | 🟢 Para APIs externas | 🟢 Común |
| Singleton | 🔴 Nunca | 🔴 Casi nunca | 🟡 Raramente |

---

## 🎯 Checklist Rápido

### Antes de empezar sesión:
```
[ ] Leo .claude/01-current-phase.md
[ ] Sé en qué etapa estoy
[ ] Sé qué voy a hacer hoy
[ ] Sé las reglas de mi etapa
```

### Durante implementación:
```
[ ] Propuse plan ANTES de implementar
[ ] Implemento un archivo a la vez
[ ] Hago review después de cada archivo
[ ] Pregunto si no estoy seguro
```

### Antes de terminar sesión:
```
[ ] test_full_flow.sh pasa
[ ] Código cumple reglas de etapa
[ ] Actualicé 01-current-phase.md
[ ] Documenté decisiones importantes
```

### Checkpoint de etapa:
```
[ ] Reviso si debo cambiar de etapa
[ ] Si cambio, leo nuevas reglas
[ ] Actualizo 01-current-phase.md con nueva etapa
[ ] Explico por qué cambié
```

---

## 🔗 Referencias Rápidas

- **¿Qué estoy construyendo?** → `.claude/00-project-brief.md`
- **¿Dónde estoy ahora?** → `.claude/01-current-phase.md`
- **¿Qué puedo hacer?** → `.claude/02-stageN-rules.md`
- **¿Cómo empiezo?** → `QUICK_START.md`
- **¿Necesito un prompt?** → `PROMPT_LIBRARY.md`
- **¿Cómo funciona todo?** → `GUIDE.md`

---

**Imprime esto y tenlo a mano mientras desarrollas** 📌
