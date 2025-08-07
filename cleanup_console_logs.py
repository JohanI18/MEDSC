#!/usr/bin/env python3
"""
Script para eliminar console.log, console.error, console.warn y console.debug
de archivos JavaScript y TypeScript
"""

import os
import re
import glob

def clean_console_logs(file_path):
    """Elimina console.log, console.error, console.warn, console.debug de un archivo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Patrones para detectar console.*
        patterns = [
            # console.log(), console.error(), etc. en líneas completas
            r'^\s*console\.(log|error|warn|debug|info)\([^)]*\);\s*\n',
            # console.* dentro de bloques catch o if
            r'\s*console\.(log|error|warn|debug|info)\([^)]*\);\s*\n',
            # console.* sin punto y coma al final
            r'\s*console\.(log|error|warn|debug|info)\([^)]*\)\s*\n',
        ]
        
        for pattern in patterns:
            content = re.sub(pattern, '', content, flags=re.MULTILINE)
        
        # Limpiar líneas vacías consecutivas
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Limpiado: {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error procesando {file_path}: {e}")
        return False

def main():
    """Función principal"""
    base_path = r"c:\Users\JSeb\Documents\2025A\Web Avanzada\New folder\Frontend"
    
    # Buscar archivos TypeScript y JavaScript
    patterns = [
        os.path.join(base_path, "**", "*.ts"),
        os.path.join(base_path, "**", "*.tsx"),
        os.path.join(base_path, "**", "*.js"),
        os.path.join(base_path, "**", "*.jsx"),
    ]
    
    files_cleaned = 0
    total_files = 0
    
    for pattern in patterns:
        for file_path in glob.glob(pattern, recursive=True):
            # Omitir archivos en node_modules
            if 'node_modules' in file_path:
                continue
                
            total_files += 1
            if clean_console_logs(file_path):
                files_cleaned += 1
    
    print(f"\n🎉 Proceso completado!")
    print(f"📁 Archivos procesados: {total_files}")
    print(f"🧹 Archivos limpiados: {files_cleaned}")

if __name__ == "__main__":
    main()
