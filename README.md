# 8-Puzzle con Búsqueda en Primero en Anchura (BFS)

Aplicación web interactiva para configurar un tablero inicial de 8-Puzzle, validar su resolubilidad y visualizar el camino óptimo encontrado por BFS.

## Instalación y ejecución

1. **Crear y activar el entorno virtual (Windows):**
   * En CMD o PowerShell:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   * En Git Bash:
     ```bash
     python -m venv venv
     source venv/Scripts/activate
     ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
     ```

3.  **Iniciar el servidor:**
    ```bash
    python app.py
    ```
    
4.  **Abrir en el navegador:**
     * Desde esta computadora:
             http://127.0.0.1:5000

     *  Desde otro dispositivo (celular, tablet u otra PC) conectado a la misma red Wi-Fi:
             Abre una terminal y ejecuta ipconfig.
             Localiza tu Dirección IPv4 en la conexión activa (por ejemplo, 192.168.1.45).
             Entra en el navegador del otro dispositivo a: http://TU_IP_IPV4:5000
