# 🛡️ AdGuard Home – Proxy de Página de Bloqueo

Este proyecto proporciona un **Servidor Proxy Inverso ligero escrito en Python**.  
Permite mostrar una **Página de Bloqueo personalizada y elegante** para los usuarios de **AdGuard Home**.

Es ideal para usuarios que ejecutan AdGuard Home en:
- Raspberry Pi
- VPS
- Servidores locales
- Android (vía Termux)

En lugar de mostrar un error de conexión genérico, el usuario verá una interfaz amigable y clara.

---

## 📋 Tabla de Contenidos

- ⚙️ Cómo Funciona
- 🧩 El Script del Servidor (`run.py`)
- 🚀 Instalación y Auto-arranque
  - 🐧 Linux (Systemd)
  - 🪟 Windows
  - 📱 Android (Termux)
  - 🍎 macOS
- 🛠️ Configuración de AdGuard Home
- ❓ Solución de Problemas

---

## ⚙️ Cómo Funciona

1. AdGuard Home bloquea un dominio (ej. `ads.google.com`).
2. En lugar de descartar el paquete, AdGuard redirige la solicitud a tu **IP local**.
3. El script de Python intercepta la solicitud en el **Puerto 80**.
4. Obtiene el contenido de una página de bloqueo alojada (Vercel, Netlify, etc.).
5. Sirve esa página al navegador, **preservando la URL original**.

🚀 Resultado: una experiencia visual limpia y profesional.

---

## 🧩 1. El Script del Servidor (`run.py`)

Crea un archivo llamado `run.py` y pega el siguiente código:

```python
import http.server
import socketserver
import urllib.request
import urllib.error

# --- CONFIGURACIÓN ---
PORT = 80
TARGET_URL = "https://unavaible-page-adguard-home.vercel.app"

class ReverseProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_proxy()

    def do_POST(self):
        self.handle_proxy()

    def handle_proxy(self):
        try:
            destination_url = TARGET_URL + self.path
            print(f"[Proxy] Solicitando: {destination_url}")

            req = urllib.request.Request(destination_url)
            req.add_header('User-Agent', 'Mozilla/5.0')

            with urllib.request.urlopen(req) as response:
                self.send_response(response.getcode())

                for key, value in response.info().items():
                    if key.lower() == "content-type":
                        self.send_header(key, value)

                self.end_headers()
                self.wfile.write(response.read())

        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
        except Exception as e:
            print(f"[ERROR] {e}")
            self.send_response(500)
            self.end_headers()

# --- INICIAR SERVIDOR ---
socketserver.TCPServer.allow_reuse_address = True

try:
    with socketserver.TCPServer(("", PORT), ReverseProxyHandler) as httpd:
        print(f"Proxy activo en http://localhost:{PORT}")
        httpd.serve_forever()
except PermissionError:
    print("El puerto 80 requiere privilegios de administrador.")
except KeyboardInterrupt:
    print("Servidor detenido.")
```
## 🚀 2. Instalación y Auto-arranque

Elige tu sistema operativo para configurar el proxy e iniciarlo automáticamente.

---

### 🐧 Opción A: Linux (Systemd) — Recomendado

Ideal para Raspberry Pi, Ubuntu, Debian y servidores sin interfaz gráfica.

#### 1️⃣ Mover el script a una ubicación permanente

```bash
sudo mkdir -p /opt/adguard-proxy
sudo cp run.py /opt/adguard-proxy/run.py
```

#### 2️⃣ Crear el servicio de systemd

```bash
sudo nano /etc/systemd/system/adguard-proxy.service
```

Pega el siguiente contenido (User=root es necesario porque el puerto 80 requiere privilegios):

```ini
[Unit]
Description=Proxy de Página de Bloqueo AdGuard Home
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/adguard-proxy
ExecStart=/usr/bin/python3 /opt/adguard-proxy/run.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

#### 3️⃣ Habilitar e iniciar el servicio

```bash
sudo systemctl daemon-reload
sudo systemctl enable adguard-proxy
sudo systemctl start adguard-proxy
```

Para comprobar el estado:

```bash
sudo systemctl status adguard-proxy
```

---

### 🪟 Opción B: Windows

#### 1️⃣ Instalar Python

Instala Python 3 y asegúrate de marcar la opción **Add Python to PATH**.

#### 2️⃣ Ejecución manual (prueba)

Abre CMD o PowerShell como Administrador, navega a la carpeta del script y ejecuta:

```powershell
python run.py
```

Es posible que Windows Firewall solicite permiso. Permite el acceso en redes privadas.

#### 3️⃣ Auto-arranque con el Programador de Tareas

1. Abre el Programador de Tareas
2. Crea una nueva tarea
3. En la pestaña General:
   - Nombre: AdGuardProxy
   - Marca **Ejecutar con los privilegios más altos**
4. En Desencadenadores:
   - Nuevo → Al iniciar el sistema
5. En Acciones:
   - Programa: `pythonw.exe`
   - Argumentos:
     ```
     C:\ruta\a\run.py
     ```

---

### 📱 Opción C: Android (Termux)

> ⚠️ Requiere acceso root o tsu, ya que Android sin root no puede usar el puerto 80.

#### 1️⃣ Instalar dependencias

```bash
pkg install python tsu termux-boot
```

#### 2️⃣ Crear directorio de arranque

```bash
mkdir -p ~/.termux/boot
```

#### 3️⃣ Crear script de inicio

```bash
nano ~/.termux/boot/start-proxy.sh
```

Contenido del archivo:

```sh
#!/data/data/com.termux/files/usr/bin/sh

termux-wake-lock

sudo python /data/data/com.termux/files/home/run.py > /data/data/com.termux/files/home/proxy_log.txt 2>&1 &
```

#### 4️⃣ Dar permisos de ejecución

```bash
chmod +x ~/.termux/boot/start-proxy.sh
```

#### 5️⃣ Activar el auto-arranque

Abre la aplicación **Termux:Boot** una vez y reinicia el dispositivo.

---

### 🍎 Opción D: macOS

#### Ejecución manual

```bash
sudo python3 ruta/a/run.py
```

#### Auto-arranque (avanzado)

Configura un servicio con **launchd** creando un archivo `.plist` en:

```bash
/Library/LaunchDaemons/
```

> ⚠️ macOS utiliza el puerto 80 para Apache por defecto.  
> Detén Apache si es necesario:

```bash
sudo apachectl stop
```
## 🛠️ 3. Configuración de AdGuard Home

Una vez que el servidor Python esté en ejecución, debes vincularlo con AdGuard Home.

### Pasos

1. Abre el **Panel de Administración de AdGuard Home**.
2. Ve a **Configuración → Configuración DNS**.
3. Desplázate hacia abajo hasta **Configuración de bloqueo DNS**.
4. Busca la opción **Modo de bloqueo**.
5. Selecciona **IP personalizada**.
6. Introduce la **dirección IP local** del dispositivo donde se ejecuta `run.py`.

### Ejemplos

- **AdGuard Home y el proxy en el mismo dispositivo**  
  Usa:
  ```
  127.0.0.1
  ```
  o la IP de la LAN (por ejemplo `192.168.1.50`).

- **AdGuard Home en un dispositivo diferente**  
  Usa la IP de la LAN del equipo donde se ejecuta el script Python.

7. Haz clic en **Guardar** para aplicar los cambios.

---

A partir de este momento, cualquier dominio bloqueado mostrará la **página de bloqueo personalizada** servida por el proxy.

