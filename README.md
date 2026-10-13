# Aplicación de impresión de etiquetas ETQ/LPN

Aplicación de demostración que valida solicitudes de impresión de etiquetas, simula su impresión y permite consultar el historial. Utiliza datos de prueba locales; no se conecta a sistemas externos ni a una impresora física.

## Requisitos

- Docker instalado y en ejecución.
- Docker Compose v2 (`docker compose`).
- Código fuente del proyecto.

## Instalación y ejecución

1. Abre una terminal en la carpeta raíz del proyecto, donde se encuentra `compose.yaml`.
2. Construye las imágenes e inicia los servicios:

   ```bash
   docker compose up --build -d
   ```

3. Comprueba que los servicios estén activos:

   ```bash
   docker compose ps
   ```

4. Abre la aplicación:

   - Interfaz: [http://localhost:4200](http://localhost:4200)
   - Documentación de la API: [http://localhost:8080/docs](http://localhost:8080/docs)

## Logs

Consulta los logs de los servicios:

```bash
docker compose logs --tail 100
```

Para seguir en vivo los logs de un servicio:

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

Pulsa `Ctrl+C` para dejar de seguir los logs; los servicios continuarán ejecutándose.

## Detener la aplicación

```bash
docker compose down
```

El historial de auditoría se guarda en el volumen Docker `print-audit` y se conserva al detener o recrear los contenedores. Para eliminar también ese volumen y su historial:

```bash
docker compose down --volumes
```
