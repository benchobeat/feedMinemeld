# Repositorio de Feeds de Inteligencia

Este repositorio está diseñado para almacenar y gestionar feeds de inteligencia de amenazas que se descargan desde fuentes locales.

## Estructura del Repositorio

- `/feeds`: Directorio principal para almacenar los feeds de inteligencia
- `/scripts`: Contiene scripts para la descarga y procesamiento de feeds
- `/docs`: Documentación relacionada con los feeds y su uso

## Configuración en Servidor Linux

### Requisitos Previos

1. Python 3.6 o superior
2. Git
3. Acceso a la red donde se encuentra el servidor de feeds (192.168.106.235)
4. Credenciales de GitHub configuradas en el servidor

### Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/benchobeat/feedMinemeld.git
   cd feedMinemeld
   ```

2. Instalar dependencias de Python:
   ```bash
   pip3 install requests python-dotenv
   ```

3. Configurar credenciales de Git (si aún no están configuradas):
   ```bash
   git config --global user.name "Tu Nombre"
   git config --global user.email "tu@email.com"
   ```

## Uso del Script de Descarga

El script principal `download_feeds.py` se encuentra en el directorio `/scripts` y maneja la descarga de feeds y actualización del repositorio.

### Descargar Feeds (sin commit/push)

```bash
python3 scripts/download_feeds.py --no-commit --no-push
```

### Descargar Feeds y Hacer Commit (sin push)

```bash
python3 scripts/download_feeds.py --no-push
```

### Descargar Feeds, Hacer Commit y Push

```bash
python3 scripts/download_feeds.py
```

### Opciones del Script

- `--no-commit`: Descarga los feeds pero no hace commit de los cambios
- `--no-push`: Hace commit pero no hace push a GitHub
- Sin opciones: Ejecuta todo el flujo completo (descarga, commit y push)

## Automatización con Cron

Para ejecutar el script periódicamente, puedes configurar una tarea programada con cron:

1. Abre el crontab del usuario:
   ```bash
   crontab -e
   ```

2. Agrega una línea para ejecutar el script cada hora (por ejemplo):
   ```
   0 * * * * cd /ruta/completa/hasta/feedMinemeld && /usr/bin/python3 scripts/download_feeds.py >> /var/log/feed_download.log 2>&1
   ```

## Estructura de Archivos de Feed

Los archivos de feed se guardan en el directorio `/feeds` con el formato `feed_YYYYMMDD_HHMMSS.csv`.

## Solución de Problemas

- **Error de certificado SSL**: Asegúrate de que el servidor tenga acceso al endpoint del feed.
- **Problemas de autenticación de Git**: Verifica que las credenciales de Git estén configuradas correctamente.
- **Problemas de red**: Verifica la conectividad con GitHub y el servidor de feeds.

## Contribución

Por favor, sigue las mejores prácticas para mantener el repositorio organizado y actualizado.