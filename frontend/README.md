# Frontend (Vite + React)

Interfaz web para visualizar el análisis del repositorio.

## Requisitos
- Node.js >= 18
- npm o pnpm/yarn

## Instalación
```bash
cd frontend
npm install
```

## Variables de entorno
Opcionalmente puedes crear un archivo `.env` en este directorio:

```
VITE_API_BASE_URL=http://localhost:8000
VITE_DEV_PORT=5173
VITE_DEV_HOST=127.0.0.1
```

Si `VITE_API_BASE_URL` no está definida, el cliente intentará usar `/api/...` y se apoyará en el proxy configurado en `vite.config.ts`.

## Scripts
- `npm run dev` – lanza Vite con hot reload.
- `npm run build` – genera la versión de producción.
- `npm run preview` – sirve el build para validación.
- `npm run lint` – ejecuta ESLint (pendiente de configurar reglas adicionales).

## Desarrollo
1. Asegúrate de que el backend FastAPI esté corriendo y accesible (ver `docs/backend_quickstart.md`).
2. Ejecuta `npm run dev`.
3. Abre el navegador en `http://localhost:5173` (o el puerto configurado).

La aplicación consume:
- `GET /tree` para poblar el árbol de archivos.
- `GET /files/{path}` para mostrar detalles.
- `POST /rescan` para forzar un escaneo.
- `GET /events` (SSE) para refrescar automáticamente los datos.
