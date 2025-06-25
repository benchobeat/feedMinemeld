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
FEED_URL = "https://192.168.106.235/feeds/IoC_IP_Output"
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
        # Construir parámetros de la URL
        params = {}
        for i, value in enumerate(FEED_PARAMS['f']):
            params[f'f[{i}]'] = value
        params['v'] = FEED_PARAMS['v']
        
        # Realizar la petición
        response = requests.get(FEED_URL, params=params, verify=False)
        response.raise_for_status()
        
        # Generar nombre de archivo con fecha y hora
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(FEEDS_DIR, f'feed_{timestamp}.csv')
        
        # Guardar el archivo
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        print(f"Feed descargado exitosamente: {filename}")
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
    parser = argparse.ArgumentParser(description='Descarga feeds de inteligencia y actualiza el repositorio.')
    parser.add_argument('--no-commit', action='store_true', help='No hacer commit de los cambios')
    parser.add_argument('--no-push', action='store_true', help='No hacer push de los cambios')
    
    args = parser.parse_args()
    
    # Asegurar que el directorio de feeds existe
    ensure_feeds_directory()
    
    # Descargar el feed
    print("Descargando feed...")
    downloaded_file = download_feed()
    
    if not downloaded_file:
        print("No se pudo descargar el feed. Saliendo.", file=sys.stderr)
        sys.exit(1)
    
    if not args.no_commit:
        # Hacer commit de los cambios
        commit_message = f"Actualización automática de feed: {os.path.basename(downloaded_file)}"
        print("\nHaciendo commit de los cambios...")
        if not run_git_command('add'):
            sys.exit(1)
            
        if not run_git_command('commit', commit_message):
            print("No se pudo hacer commit de los cambios.", file=sys.stderr)
            sys.exit(1)
        
        if not args.no_push:
            # Hacer push de los cambios
            print("\nSubiendo cambios a GitHub...")
            if not run_git_command('push'):
                print("No se pudo subir los cambios a GitHub.", file=sys.stderr)
                sys.exit(1)
    
    print("\nProceso completado exitosamente.")

if __name__ == "__main__":
    main()
