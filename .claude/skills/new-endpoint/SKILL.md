---
name: new-endpoint
description: Crea un endpoint completo (modelo → servicio → ruta → test) siguiendo las convenciones del proyecto. Usar cuando se pida agregar una ruta o endpoint nuevo a la API.
---

# Skill: Nuevo Endpoint

## Objetivo
Crear un endpoint completo siguiendo las convenciones del proyecto.
Aplica para Flask (Python) y Express (Node.js).

## Cómo activar
```
Usa el skill new-endpoint para crear [método] /[ruta] que [descripción]
```
Ejemplo:
```
Usa el skill new-endpoint para crear POST /api/invoices que registre una factura nueva
```

## Flujo de creación

Siempre en este orden:
1. Modelo (si es entidad nueva)
2. Servicio (lógica de negocio)
3. Ruta / Controlador
4. Test
5. Actualizar documentación

---

## Patrón Flask

### Modelo (SQLAlchemy)
```python
# src/models/nombre.py
from app import db
from datetime import datetime

class NombreModelo(db.Model):
    __tablename__ = 'nombre_tabla'

    id = db.Column(db.Integer, primary_key=True)
    # campos...
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            # campos...
        }
```

### Servicio
```python
# src/services/nombre_service.py
from src.models.nombre import NombreModelo
from app import db

def crear_nombre(data: dict) -> dict:
    try:
        item = NombreModelo(**data)
        db.session.add(item)
        db.session.commit()
        return item.to_dict()
    except Exception as e:
        db.session.rollback()
        raise e

def obtener_nombre(id: int) -> dict | None:
    item = db.session.get(NombreModelo, id)
    return item.to_dict() if item else None
```

### Ruta
```python
# src/api/nombre_routes.py
from flask import Blueprint, request, jsonify
from src.services import nombre_service

nombre_bp = Blueprint('nombre', __name__, url_prefix='/api/nombre')

@nombre_bp.route('/', methods=['POST'])
def crear():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos requeridos'}), 400
    try:
        resultado = nombre_service.crear_nombre(data)
        return jsonify(resultado), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@nombre_bp.route('/<int:id>', methods=['GET'])
def obtener(id):
    item = nombre_service.obtener_nombre(id)
    if not item:
        return jsonify({'error': 'No encontrado'}), 404
    return jsonify(item), 200
```

---

## Patrón Express

### Modelo (si usas Sequelize)
```javascript
// src/models/nombre.model.js
const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const Nombre = sequelize.define('Nombre', {
  // campos...
}, { timestamps: true });

module.exports = Nombre;
```

### Servicio
```javascript
// src/services/nombre.service.js
const Nombre = require('../models/nombre.model');

const crear = async (data) => {
  return await Nombre.create(data);
};

const obtenerPorId = async (id) => {
  return await Nombre.findByPk(id);
};

module.exports = { crear, obtenerPorId };
```

### Ruta
```javascript
// src/api/nombre.routes.js
const express = require('express');
const router = express.Router();
const nombreService = require('../services/nombre.service');

router.post('/', async (req, res) => {
  try {
    const item = await nombreService.crear(req.body);
    res.status(201).json(item);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/:id', async (req, res) => {
  const item = await nombreService.obtenerPorId(req.params.id);
  if (!item) return res.status(404).json({ error: 'No encontrado' });
  res.json(item);
});

module.exports = router;
```

---

## Estructura de respuesta estándar

### Éxito
```json
{
  "data": { ... },
  "message": "Operación exitosa"
}
```

### Error
```json
{
  "error": "Descripción del error",
  "details": "Información adicional (solo en desarrollo)"
}
```

## Códigos HTTP a usar
| Situación | Código |
|---|---|
| GET exitoso | 200 |
| POST exitoso (creó recurso) | 201 |
| Datos inválidos / faltantes | 400 |
| No autenticado | 401 |
| Sin permisos | 403 |
| No encontrado | 404 |
| Error del servidor | 500 |
