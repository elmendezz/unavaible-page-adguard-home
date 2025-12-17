# unavaible-page-adguard-home
AdGuard Home Custom Page Blocked Custom

----

# How To Implementa
Create a Python server that starts on port 80 and redirects you.
```import http.server
import socketserver
import urllib.request
import urllib.error
import sys

# CONFIGURACIÓN
PORT = 80
# La URL exacta de tu proyecto en Vercel
TARGET_URL = "https://unavaible-page-adguard-home.vercel.app"

class ReverseProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_proxy()

    def do_POST(self):
        self.handle_proxy()

    def handle_proxy(self):
        try:
            # 1. Construir la URL destino manteniendo la ruta (ej: /imagen.png)
            url_destino = TARGET_URL + self.path
            
            # Imprimir log para depuración
            print(f"[Proxy] Solicitando: {url_destino}")

            # 2. Crear la solicitud al servidor original
            # Se añade un User-Agent genérico para evitar bloqueos simples
            req = urllib.request.Request(url_destino)
            req.add_header('User-Agent', 'Mozilla/5.0')

            # 3. Obtener la respuesta de Vercel
            with urllib.request.urlopen(req) as response:
                # Enviar el código de estado original (200, 404, etc.)
                self.send_response(response.getcode())

                # 4. Copiar las cabeceras importantes (Content-Type es vital para que cargue CSS/JS)
                headers_to_pass = ['Content-Type', 'Date', 'Server']
                for key, value in response.info().items():
                    if key in headers_to_pass:
                        self.send_header(key, value)
                
                # Importante para cerrar la cabecera
                self.end_headers()

                # 5. Enviar el contenido real (HTML, imágenes, CSS) al cliente
                self.wfile.write(response.read())

        except urllib.error.HTTPError as e:
            # Manejar errores como 404 (Página no encontrada) del destino
            self.send_response(e.code)
            self.end_headers()
            print(f"[!] Error remoto: {e.code}")
        except Exception as e:
            # Manejar errores de conexión
            print(f"[!] Error interno: {e}")
            if not False: # Simulación de chequeo de estado
                self.send_response(500)
                self.end_headers()

# INICIAR SERVIDOR
try:
    # Permitir reutilizar el puerto inmediatamente si se cierra forzosamente
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), ReverseProxyHandler) as httpd:
        print(f"--- PROXY INVERSO ACTIVO ---")
        print(f"Escuchando en: http://localhost:{PORT}")
        print(f"Sirviendo contenido oculto de: {TARGET_URL}")
        print("La barra de direcciones NO cambiará.")
        httpd.serve_forever()

except PermissionError:
    print(f"\n[ERROR] El puerto {PORT} requiere permisos de superusuario.")
    print("Ejecuta este script con: sudo python proxy.py")
except KeyboardInterrupt:
    print("\nServidor detenido.") 
  ```

 jejeje