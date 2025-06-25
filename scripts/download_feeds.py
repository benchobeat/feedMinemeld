#!/usr/bin/env python3
"""
Script para descargar feeds de inteligencia de amenazas desde una URL y actualizar el repositorio.
"""
import os
import sys
import argparse
import requests
import datetime
import subprocess
from urllib3.exceptions import InsecureRequestWarning

# Deshabilitar advertencias de certificado SSL no verificado
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Configuración
FEEDS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'feeds')

# Obtener la URL del feed desde variable de entorno o usar valor por defecto
FEED_URL = os.environ.get('FEED_URL', 'https://192.168.106.235/feeds/IoC_IP_Output')

# Validar que la URL del feed esté configurada
if not FEED_URL:
    print("[ERROR] La URL del feed no está configurada. Por favor, establece la variable de entorno FEED_URL.")
    sys.exit(1)

FEED_PARAMS = {
    'v': 'csv',
    'f': [
        'indicator|ioc',
        'iocType',
        'mail|response',
        'mail',
        'origin',
        'requester|Requester',
        'stix_title|info',
        'confidence',
        'risk'
    ]
}

def ensure_feeds_directory():
    """Asegura que el directorio de feeds exista."""
    if not os.path.exists(FEEDS_DIR):
        os.makedirs(FEEDS_DIR)

def download_feed():
    """Descarga el feed desde la URL especificada."""
    try:
        print("\n" + "="*50)
        print("Iniciando descarga del feed...")
        print(f"Hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Construir parámetros de la URL manualmente para mantener el formato correcto
        params = 'v=csv&f=indicator|ioc&f=iocType&f=mail|response&f=mail&f=origin&f=requester|Requester&f=stix_title|info&f=confidence&f=risk'
        full_url = f"{FEED_URL}?{params}"
        
        print("\n[DEBUG] Configuración de la solicitud:")
        print(f"- URL base: {FEED_URL}")
        print(f"- Parámetros: {params}")
        print(f"- URL completa: {full_url}")
        
        # Configurar headers para indicar que esperamos un CSV
        headers = {
            'Accept': 'text/csv',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print("\n[DEBUG] Headers de la solicitud:")
        for key, value in headers.items():
            print(f"- {key}: {value}")
        
        print("\n[INFO] Realizando petición HTTP...")
        response = requests.get(full_url, headers=headers, verify=False)
        
        print("\n[DEBUG] Información de la respuesta:")
        print(f"- Código de estado: {response.status_code}")
        print(f"- Content-Type: {response.headers.get('Content-Type', 'No especificado')}")
        print(f"- Tamaño de la respuesta: {len(response.content)} bytes")
        print(f"- Primeros 200 caracteres de la respuesta: {response.text[:200]}")
        
        # Verificar código de estado
        response.raise_for_status()
        
        # Verificar que el contenido sea efectivamente un CSV
        content_type = response.headers.get('Content-Type', '').lower()
        is_csv = 'text/csv' in content_type or 'application/csv' in content_type
        
        print("\n[DEBUG] Análisis del contenido:")
        print(f"- ¿Es CSV? {'Sí' if is_csv else 'No'}")
        if not is_csv:
            print("  - Advertencia: El Content-Type no indica que sea un archivo CSV")
            print(f"  - Content-Type recibido: {content_type}")
        
        # Contar líneas del CSV
        line_count = len(response.text.splitlines())
        print(f"- Número de líneas en el CSV: {line_count}")
        
        if line_count > 0:
            # Mostrar encabezados
            headers = response.text.splitlines()[0].split(',')
            print(f"- Columnas detectadas ({len(headers)}): {', '.join(headers[:5])}{'...' if len(headers) > 5 else ''}")
        
        # Generar nombre de archivo con fecha y hora
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(FEEDS_DIR, f'feed_{timestamp}.csv')
        
        print(f"\n[INFO] Guardando archivo en: {filename}")
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Guardar el archivo
        with open(filename, 'w', encoding='utf-8-sig') as f:  # utf-8-sig para manejar BOM si es necesario
            f.write(response.text)
            
        # Verificar que el archivo se haya guardado correctamente
        file_size = os.path.getsize(filename)
        print(f"[ÉXITO] Archivo guardado correctamente")
        print(f"- Tamaño del archivo: {file_size} bytes")
        print(f"- Líneas escritas: {line_count}")
        print("="*50 + "\n")
        
        return filename
        
    except requests.exceptions.RequestException as e:
        print(f"Error al descargar el feed: {e}", file=sys.stderr)
        return None

git_commands = {
    'add': ['git', 'add', '.'],
    'commit': ['git', 'commit', '-m'],
    'push': ['git', 'push', 'origin', 'main']
}

def run_git_command(command, *args):
    """Ejecuta un comando de Git."""
    try:
        cmd = git_commands[command].copy()
        if command == 'commit' and args:
            cmd.append(args[0])
        
        result = subprocess.run(
            cmd,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar 'git {command}': {e}", file=sys.stderr)
        print(f"Salida de error: {e.stderr}", file=sys.stderr)
        return False

def main():
    global FEED_URL
    
    parser = argparse.ArgumentParser(description='Descarga feeds de inteligencia y actualiza el repositorio.')
    parser.add_argument('--no-commit', action='store_true', help='No hacer commit de los cambios')
    parser.add_argument('--no-push', action='store_true', help='No hacer push a GitHub')
    parser.add_argument('--debug', action='store_true', help='Mostrar información de depuración')
    parser.add_argument('--feed-url', type=str, help='URL del feed (sobreescribe la variable de entorno FEED_URL)')
    
    args = parser.parse_args()
    
    try:
        # Usar la URL del argumento de línea de comandos si se proporciona
        if args.feed_url:
            global FEED_URL
            FEED_URL = args.feed_url
            print(f"[INFO] Usando URL del feed proporcionada por línea de comandos")
        else:
            print(f"[INFO] Usando URL del feed de la variable de entorno FEED_URL")
            
        print(f"[DEBUG] URL del feed: {FEED_URL}")
        
        # Asegurar que el directorio de feeds existe
        ensure_feeds_directory()
        
        # Descargar el feed
        print("\n" + "="*50)
        print("INICIANDO PROCESO DE ACTUALIZACIÓN DE FEEDS")
        print("="*50)
        
        downloaded_file = download_feed()
        
        if not downloaded_file:
            print("\n[ERROR] No se pudo descargar el feed. Abortando proceso.")
            sys.exit(1)
            
        print("\n[ÉXITO] Feed descargado correctamente")
        print(f"- Archivo: {downloaded_file}")
        
        # Verificar si hay cambios para hacer commit
        if not args.no_commit:
            # Obtener el nombre del archivo para el mensaje de commit
            filename = os.path.basename(downloaded_file)
            commit_message = f"feat: actualización automática de feed {filename}"
            
            print("\n" + "-"*50)
            print("PROCESO DE COMMIT")
            print("-"*50)
            
            # Agregar archivos al staging
            print("\n[INFO] Agregando archivos al área de staging...")
            if not run_git_command('add'):
                print("[ERROR] No se pudieron agregar los archivos al staging")
                sys.exit(1)
                
            # Verificar si hay cambios para hacer commit
            check_changes = subprocess.run(
                ['git', 'diff-index', '--quiet', 'HEAD', '--'],
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            
            if check_changes.returncode != 0:
                # Hacer commit de los cambios
                print("[INFO] Haciendo commit de los cambios...")
                if run_git_command('commit', commit_message):
                    print(f"[ÉXITO] Commit realizado: {commit_message}")
                    
                    # Hacer push si está habilitado
                    if not args.no_push:
                        print("\n" + "-"*50)
                        print("SUBIDA DE CAMBIOS A GITHUB")
                        print("-"*50)
                        print("\n[INFO] Subiendo cambios a GitHub...")
                        if run_git_command('push'):
                            print("[ÉXITO] Cambios subidos exitosamente a GitHub")
                        else:
                            print("[ADVERTENCIA] No se pudieron subir los cambios a GitHub")
                else:
                    print("[ERROR] No se pudo hacer commit de los cambios")
            else:
                print("[INFO] No hay cambios para hacer commit")
        
        print("\n" + "="*50)
        print("PROCESO COMPLETADO EXITOSAMENTE")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\n[ERROR CRÍTICO] {str(e)}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
