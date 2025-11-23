"""
Script de Compilación Automática - Aplicación IRC
Compila la aplicación y prepara el paquete de distribución
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime
import json

class CompiladorApp:
    """Gestor de compilación y empaquetado"""
    
    def __init__(self):
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.dist_dir = os.path.join(self.project_dir, 'dist')
        self.build_dir = os.path.join(self.project_dir, 'build')
        self.package_dir = None
        
    def print_header(self, text):
        """Imprime un header decorado"""
        print()
        print("=" * 60)
        print(f"  {text}")
        print("=" * 60)
        print()
    
    def print_step(self, text):
        """Imprime un paso"""
        print(f"\n▶ {text}")
    
    def print_success(self, text):
        """Imprime mensaje de éxito"""
        print(f"  ✅ {text}")
    
    def print_error(self, text):
        """Imprime mensaje de error"""
        print(f"  ❌ {text}")
    
    def print_warning(self, text):
        """Imprime mensaje de advertencia"""
        print(f"  ⚠️  {text}")
    
    def verificar_archivos_necesarios(self):
        """Verifica que existan todos los archivos necesarios"""
        self.print_step("Verificando archivos necesarios...")
        
        archivos_requeridos = {
            'main.py': 'Archivo principal de la aplicación',
            'irc_app.spec': 'Archivo de configuración de PyInstaller',
            'config/service_account.json': 'Credenciales de Google (⚠️  CRÍTICO)',
            'config/app_config.json': 'Configuración de la aplicación',
            'resources/irc_icon.ico': 'Icono de la aplicación',
        }
        
        archivos_opcionales = {
            'resources/irc_logo.png': 'Logo de la aplicación',
            'resources/irc_logo_header.png': 'Logo para header',
            'README_DISTRIBUCION.txt': 'Instrucciones de instalación',
        }
        
        todos_ok = True
        
        # Verificar archivos requeridos
        for archivo, descripcion in archivos_requeridos.items():
            path = os.path.join(self.project_dir, archivo)
            if os.path.exists(path):
                self.print_success(f"{archivo}")
            else:
                self.print_error(f"{archivo} - {descripcion}")
                todos_ok = False
        
        # Verificar archivos opcionales
        for archivo, descripcion in archivos_opcionales.items():
            path = os.path.join(self.project_dir, archivo)
            if os.path.exists(path):
                self.print_success(f"{archivo} (opcional)")
            else:
                self.print_warning(f"{archivo} - {descripcion} (opcional)")
        
        return todos_ok
    
    def verificar_dependencias(self):
        """Verifica que estén instaladas las dependencias de Python"""
        self.print_step("Verificando dependencias de Python...")
        
        dependencias = [
            'gspread',
            'google-auth',
            'PIL',
            'reportlab',
            'PyPDF2',
            'pyinstaller'
        ]
        
        faltantes = []
        
        for dep in dependencias:
            try:
                if dep == 'PIL':
                    import PIL
                elif dep == 'google-auth':
                    import google.auth
                elif dep == 'pyinstaller':
                    import PyInstaller
                else:
                    __import__(dep)
                
                self.print_success(dep)
            except ImportError:
                self.print_error(f"{dep} - NO INSTALADO")
                faltantes.append(dep)
        
        if faltantes:
            print()
            print("Para instalar las dependencias faltantes:")
            print(f"  pip install {' '.join(faltantes)}")
            return False
        
        return True
    
    def verificar_configuracion(self):
        """Verifica la configuración de la aplicación"""
        self.print_step("Verificando configuración...")
        
        config_path = os.path.join(self.project_dir, 'config', 'app_config.json')
        
        if not os.path.exists(config_path):
            self.print_error("No se encontró app_config.json")
            return False
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Verificar campos importantes
            sheet_id = config.get('google_sheet_id', '')
            
            if not sheet_id or sheet_id == 'TU_ID_DE_GOOGLE_SHEET_AQUI':
                self.print_warning("El google_sheet_id no está configurado en app_config.json")
                print("    Por favor, actualiza este valor antes de distribuir")
            else:
                self.print_success(f"Google Sheet ID configurado")
            
            return True
            
        except Exception as e:
            self.print_error(f"Error leyendo configuración: {e}")
            return False
    
    def limpiar_directorios_previos(self):
        """Limpia directorios de compilaciones anteriores"""
        self.print_step("Limpiando compilaciones anteriores...")
        
        dirs_to_clean = [self.dist_dir, self.build_dir]
        
        for dir_path in dirs_to_clean:
            if os.path.exists(dir_path):
                try:
                    shutil.rmtree(dir_path)
                    self.print_success(f"Eliminado: {os.path.basename(dir_path)}/")
                except Exception as e:
                    self.print_warning(f"No se pudo eliminar {dir_path}: {e}")
    
    def compilar_aplicacion(self):
        """Compila la aplicación usando PyInstaller"""
        self.print_step("Compilando aplicación con PyInstaller...")
        
        spec_file = os.path.join(self.project_dir, 'irc_app.spec')
        
        if not os.path.exists(spec_file):
            self.print_error("No se encontró irc_app.spec")
            return False
        
        try:
            # Ejecutar PyInstaller
            result = subprocess.run(
                ['pyinstaller', '--clean', 'irc_app.spec'],
                cwd=self.project_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.print_success("Compilación exitosa")
                
                # Verificar que se creó el ejecutable
                exe_path = os.path.join(self.dist_dir, 'Gestion_IRC.exe')
                if os.path.exists(exe_path):
                    size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                    self.print_success(f"Ejecutable creado: Gestion_IRC.exe ({size_mb:.1f} MB)")
                    return True
                else:
                    self.print_error("El ejecutable no se creó correctamente")
                    return False
            else:
                self.print_error("Error en la compilación")
                print("\n" + result.stderr)
                return False
                
        except Exception as e:
            self.print_error(f"Error ejecutando PyInstaller: {e}")
            return False
    
    def crear_paquete_distribucion(self):
        """Crea un paquete completo para distribución"""
        self.print_step("Creando paquete de distribución...")
        
        # Crear nombre del paquete con fecha
        fecha = datetime.now().strftime('%Y%m%d')
        package_name = f'IRC_App_v1.0_{fecha}'
        self.package_dir = os.path.join(self.project_dir, package_name)
        
        # Crear directorio del paquete
        os.makedirs(self.package_dir, exist_ok=True)
        
        # Copiar ejecutable
        exe_src = os.path.join(self.dist_dir, 'Gestion_IRC.exe')
        exe_dst = os.path.join(self.package_dir, 'Gestion_IRC.exe')
        
        if os.path.exists(exe_src):
            shutil.copy2(exe_src, exe_dst)
            self.print_success("Ejecutable copiado")
        else:
            self.print_error("No se encontró el ejecutable")
            return False
        
        # Copiar carpeta config
        config_src = os.path.join(self.project_dir, 'config')
        config_dst = os.path.join(self.package_dir, 'config')
        
        if os.path.exists(config_src):
            shutil.copytree(config_src, config_dst)
            self.print_success("Configuración copiada")
        else:
            self.print_warning("No se encontró la carpeta config")
        
        # Copiar recursos si no están empaquetados
        resources_src = os.path.join(self.project_dir, 'resources')
        if os.path.exists(resources_src):
            resources_dst = os.path.join(self.package_dir, 'resources')
            shutil.copytree(resources_src, resources_dst)
            self.print_success("Recursos copiados")
        
        # Copiar README
        readme_src = os.path.join(self.project_dir, 'README_DISTRIBUCION.txt')
        if os.path.exists(readme_src):
            readme_dst = os.path.join(self.package_dir, 'LEEME.txt')
            shutil.copy2(readme_src, readme_dst)
            self.print_success("Instrucciones copiadas")
        
        # Crear archivo de versión
        version_info = {
            'version': '1.0.0',
            'fecha_compilacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'python_version': sys.version,
        }
        
        version_file = os.path.join(self.package_dir, 'VERSION.json')
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(version_info, f, indent=2, ensure_ascii=False)
        
        self.print_success(f"Paquete creado: {package_name}/")
        
        return True
    
    def crear_zip(self):
        """Crea un archivo ZIP del paquete"""
        self.print_step("Creando archivo ZIP...")
        
        if not self.package_dir or not os.path.exists(self.package_dir):
            self.print_error("No se encontró el directorio del paquete")
            return False
        
        try:
            zip_name = os.path.basename(self.package_dir)
            zip_path = os.path.join(self.project_dir, f'{zip_name}.zip')
            
            # Crear ZIP
            shutil.make_archive(
                os.path.join(self.project_dir, zip_name),
                'zip',
                self.project_dir,
                zip_name
            )
            
            if os.path.exists(zip_path):
                size_mb = os.path.getsize(zip_path) / (1024 * 1024)
                self.print_success(f"ZIP creado: {zip_name}.zip ({size_mb:.1f} MB)")
                return True
            else:
                self.print_error("No se pudo crear el archivo ZIP")
                return False
                
        except Exception as e:
            self.print_error(f"Error creando ZIP: {e}")
            return False
    
    def mostrar_resumen(self):
        """Muestra un resumen de la compilación"""
        self.print_header("RESUMEN")
        
        print("✅ Compilación completada exitosamente")
        print()
        print("Archivos generados:")
        
        if self.package_dir and os.path.exists(self.package_dir):
            print(f"  📁 Carpeta: {os.path.basename(self.package_dir)}/")
            print(f"  📦 ZIP: {os.path.basename(self.package_dir)}.zip")
        
        print()
        print("Próximos pasos:")
        print("  1. Probar el ejecutable en tu equipo")
        print("  2. Probar en otro equipo Windows limpio")
        print("  3. Distribuir el archivo ZIP a los usuarios")
        print()
        print("Recordatorios:")
        print("  ⚠️  Verificar que service_account.json esté incluido")
        print("  ⚠️  Verificar que google_sheet_id esté configurado")
        print("  ⚠️  La hoja debe estar compartida con la cuenta de servicio")
        print()
    
    def compilar(self):
        """Ejecuta el proceso completo de compilación"""
        self.print_header("COMPILACIÓN - APLICACIÓN IRC")
        
        # Verificaciones previas
        if not self.verificar_archivos_necesarios():
            self.print_error("Faltan archivos necesarios")
            return False
        
        if not self.verificar_dependencias():
            self.print_error("Faltan dependencias")
            return False
        
        if not self.verificar_configuracion():
            self.print_error("Problemas con la configuración")
            return False
        
        # Confirmación
        print()
        respuesta = input("¿Continuar con la compilación? (s/n): ").lower().strip()
        
        if respuesta != 's':
            print("\nCompilación cancelada")
            return False
        
        # Proceso de compilación
        self.limpiar_directorios_previos()
        
        if not self.compilar_aplicacion():
            return False
        
        if not self.crear_paquete_distribucion():
            return False
        
        if not self.crear_zip():
            return False
        
        # Resumen
        self.mostrar_resumen()
        
        return True


def main():
    """Función principal"""
    compilador = CompiladorApp()
    
    try:
        exito = compilador.compilar()
        
        if exito:
            print()
            print("=" * 60)
            print("  ✅ ¡PROCESO COMPLETADO CON ÉXITO!")
            print("=" * 60)
            sys.exit(0)
        else:
            print()
            print("=" * 60)
            print("  ❌ HUBO ERRORES EN LA COMPILACIÓN")
            print("=" * 60)
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
