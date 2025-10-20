# Test Data Management

## Descripción
Estrategia para gestionar datos de prueba de forma mantenible y realista.

## Prompt
```
Necesito estrategia para datos de prueba en [proyecto]:

SITUACIÓN ACTUAL:
- ¿Qué tipo de datos necesito? [usuarios, transacciones, configs, etc]
- ¿Cuántos casos de prueba? [cantidad aproximada]
- ¿Los datos cambian frecuentemente? [sí/no]

OPCIONES A CONSIDERAR:
1. **Fixtures estáticos** (JSON/YAML)
   - Pros: Simple, versionable, rápido
   - Contras: Puede quedar obsoleto

2. **Factory functions** (generar programáticamente)
   - Pros: Flexible, datos variados
   - Contras: Más código, puede ser no determinístico

3. **Seeding de BD** (scripts de inicialización)
   - Pros: Datos realistas, relaciones correctas
   - Contras: Setup más complejo

4. **Copias de producción** (sanitizadas)
   - Pros: Muy realistas
   - Contras: Privacidad, tamaño

Propón estrategia apropiada para mi caso con ejemplos.
```

## Tags
- Categoría: testing
- Dificultad: intermedio
- Stage: 2, 3
