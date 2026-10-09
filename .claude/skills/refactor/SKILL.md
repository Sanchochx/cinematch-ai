---
name: refactor
description: Refactoriza código sin cambiar su comportamiento (funciones largas, duplicación, N+1, magic numbers). Usar cuando se pida mejorar, limpiar o reestructurar código existente.
---

# Skill: Refactorizar Código

## Objetivo
Mejorar la calidad del código existente sin cambiar su comportamiento.
Aplica para Python/Flask y Node.js/Express.

## Cómo activar
```
Usa el skill refactor en [archivo] enfocándote en [aspecto opcional]
```
Ejemplos:
```
Usa el skill refactor en src/api/invoices.py
Usa el skill refactor en src/services/user_service.py enfocándote en manejo de errores
```

## Proceso

1. **Analizar** el código actual e identificar problemas
2. **Listar** los cambios propuestos antes de hacerlos
3. **Confirmar** que los tests siguen pasando después del refactor
4. **Documentar** si se cambió alguna interfaz pública

---

## Señales que indican necesidad de refactor

### Funciones muy largas (+30 líneas)
```python
# ❌ Antes
def procesar_pedido(data):
    # 50 líneas mezclando validación, lógica y DB

# ✅ Después
def procesar_pedido(data):
    datos_validados = _validar_pedido(data)
    totales = _calcular_totales(datos_validados)
    return _guardar_pedido(totales)
```

### Lógica duplicada
```python
# ❌ Antes: misma validación en 3 rutas distintas
if not data.get('email') or '@' not in data['email']:
    return jsonify({'error': 'Email inválido'}), 400

# ✅ Después: extraer a util
from src.utils.validators import validar_email
```

### Manejo de errores inconsistente
```python
# ❌ Antes
try:
    resultado = servicio.crear(data)
except:          # captura todo, oculta bugs
    pass

# ✅ Después
try:
    resultado = servicio.crear(data)
except ValueError as e:
    return jsonify({'error': str(e)}), 400
except Exception as e:
    logger.error(f"Error inesperado: {e}")
    return jsonify({'error': 'Error interno'}), 500
```

### Magic numbers y strings
```python
# ❌ Antes
if user.role == 3:
    ...
if len(password) < 8:
    ...

# ✅ Después
ROLE_ADMIN = 3
MIN_PASSWORD_LENGTH = 8
```

### Queries N+1
```python
# ❌ Antes
pedidos = Pedido.query.all()
for pedido in pedidos:
    print(pedido.cliente.nombre)  # query por cada pedido

# ✅ Después
pedidos = Pedido.query.options(joinedload(Pedido.cliente)).all()
```

---

## Checklist post-refactor

- [ ] Los tests existentes siguen pasando
- [ ] El comportamiento observable es idéntico
- [ ] No se introdujeron dependencias nuevas innecesarias
- [ ] Los nombres son más claros que antes
- [ ] El código es más fácil de leer de arriba a abajo

## Formato de respuesta

```
ANÁLISIS: [descripción de los problemas encontrados]

CAMBIOS PROPUESTOS:
1. [cambio] — [razón]
2. [cambio] — [razón]

[código refactorizado]

VERIFICACIÓN: [confirmar que lógica es equivalente]
```
