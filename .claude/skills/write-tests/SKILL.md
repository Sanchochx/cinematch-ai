---
name: write-tests
description: Genera tests (caso feliz, datos inválidos, casos límite, mocks de servicios externos) con pytest o Jest. Usar cuando se pida escribir o ampliar tests de un archivo o función.
---

# Skill: Escribir Tests

## Objetivo
Generar tests completos y útiles para el código existente.
Aplica para pytest (Python/Flask) y Jest (Node.js/Express).

## Cómo activar
```
Usa el skill write-tests para [archivo o función]
```
Ejemplo:
```
Usa el skill write-tests para src/services/invoice_service.py
```

## Qué cubrir siempre

Para cada función o endpoint, generar tests para:
1. **Caso feliz** — funciona con datos válidos
2. **Datos inválidos** — qué pasa con inputs incorrectos
3. **Caso vacío / null** — qué pasa sin datos
4. **Caso límite** — valores extremos (0, negativos, strings vacíos)
5. **Error de servidor** — simular fallo de DB u otro servicio

---

## Patrón pytest (Flask)

```python
# tests/test_nombre_service.py
import pytest
from unittest.mock import patch, MagicMock
from src.services.nombre_service import crear_nombre, obtener_nombre

class TestCrearNombre:
    def test_crea_correctamente_con_datos_validos(self, app):
        """Caso feliz: crea el recurso y retorna diccionario"""
        data = {'campo': 'valor'}
        resultado = crear_nombre(data)
        assert resultado['campo'] == 'valor'
        assert 'id' in resultado

    def test_falla_con_datos_faltantes(self, app):
        """Valida que lanza excepción si faltan campos requeridos"""
        with pytest.raises(Exception):
            crear_nombre({})

    def test_falla_si_db_no_disponible(self, app):
        """Simula fallo de base de datos"""
        with patch('src.services.nombre_service.db.session.commit') as mock:
            mock.side_effect = Exception('DB error')
            with pytest.raises(Exception, match='DB error'):
                crear_nombre({'campo': 'valor'})


class TestObtenerNombre:
    def test_retorna_item_existente(self, app):
        resultado = obtener_nombre(1)
        assert resultado is not None
        assert resultado['id'] == 1

    def test_retorna_none_si_no_existe(self, app):
        resultado = obtener_nombre(99999)
        assert resultado is None


# Fixture base (en conftest.py si no existe)
# @pytest.fixture
# def app():
#     from app import create_app
#     app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
#     with app.app_context():
#         db.create_all()
#         yield app
#         db.drop_all()
```

### Para endpoints (con test client)
```python
# tests/test_nombre_routes.py
def test_post_crea_recurso(client):
    response = client.post('/api/nombre/', json={'campo': 'valor'})
    assert response.status_code == 201
    assert response.json['campo'] == 'valor'

def test_post_falla_sin_datos(client):
    response = client.post('/api/nombre/', json={})
    assert response.status_code == 400

def test_get_retorna_404_si_no_existe(client):
    response = client.get('/api/nombre/99999')
    assert response.status_code == 404
```

---

## Patrón Jest (Express)

```javascript
// tests/nombre.service.test.js
const nombreService = require('../src/services/nombre.service');
const Nombre = require('../src/models/nombre.model');

jest.mock('../src/models/nombre.model');

describe('NombreService', () => {
  afterEach(() => jest.clearAllMocks());

  describe('crear', () => {
    test('crea correctamente con datos válidos', async () => {
      const mockData = { campo: 'valor' };
      Nombre.create.mockResolvedValue({ id: 1, ...mockData });

      const resultado = await nombreService.crear(mockData);

      expect(resultado.id).toBe(1);
      expect(resultado.campo).toBe('valor');
    });

    test('lanza error si falla la DB', async () => {
      Nombre.create.mockRejectedValue(new Error('DB error'));
      await expect(nombreService.crear({})).rejects.toThrow('DB error');
    });
  });

  describe('obtenerPorId', () => {
    test('retorna null si no existe', async () => {
      Nombre.findByPk.mockResolvedValue(null);
      const resultado = await nombreService.obtenerPorId(99999);
      expect(resultado).toBeNull();
    });
  });
});
```

### Para endpoints con supertest
```javascript
// tests/nombre.routes.test.js
const request = require('supertest');
const app = require('../src/app');

describe('POST /api/nombre', () => {
  test('201 con datos válidos', async () => {
    const res = await request(app).post('/api/nombre').send({ campo: 'valor' });
    expect(res.status).toBe(201);
    expect(res.body.campo).toBe('valor');
  });

  test('400 sin datos', async () => {
    const res = await request(app).post('/api/nombre').send({});
    expect(res.status).toBe(400);
  });
});
```

---

## Reglas al generar tests
- Cada test tiene una sola assertion principal
- Los nombres describen qué se está probando: `test_retorna_404_si_no_existe`
- Usar mocks para aislar servicios externos (DB, APIs)
- No depender del orden de ejecución de los tests
- Limpiar el estado después de cada test (`afterEach`, fixtures)
