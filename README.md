# 📚 Biblioteca Digital

Sistema de Gestión de Biblioteca Digital desarrollado con Django 6. Permite administrar libros, autores, categorías, préstamos, reservas y sanciones, con un panel de control con gráficos estadísticos y exportación de reportes.

---

## Roles de usuario

### 📖 Lector
- Puede: ver catálogo, buscar libros, reservar, ver sus préstamos y reservas, ver su perfil.
- No puede: crear/editar/eliminar libros, ver reportes generales, gestionar usuarios.
- Panel: `/dashboard/lector/`
- Login demo: `lector_juan` / `Lector1234!`

### 🏛️ Bibliotecario
- Puede: todo lo anterior + gestionar libros, autores, categorías, préstamos de todos, reportes PDF/Excel/CSV, gestión de usuarios.
- Panel: `/dashboard/`
- Login demo: `admin_bib` / `Admin1234!`

---

## Inicio de sesión por roles

En la pantalla `/accounts/login/` hay dos pestañas:
- **Lector** → verifica que la cuenta tenga rol "lector" → redirige a `/dashboard/lector/`
- **Bibliotecario** → verifica que la cuenta tenga rol "bibliotecario" → redirige a `/dashboard/`

Si se selecciona "Bibliotecario" pero la cuenta es Lector, se muestra:
> "Tu cuenta no tiene permisos de bibliotecario."

---

## Funcionalidades

| Módulo | Descripción |
|---|---|
| **Autenticación** | Registro con selector de rol, login con pestañas por rol, logout |
| **Roles** | Lector y Bibliotecario — paneles y permisos completamente diferenciados |
| **Catálogo** | CRUD completo de libros, autores y categorías |
| **Préstamos** | Registro, seguimiento y devolución de préstamos |
| **Reservas** | Reserva de libros con expiración automática |
| **Sanciones** | Detección de retrasos y marcado automático de usuarios |
| **Dashboard Bibliotecario** | Panel con 7 stat-cards + 3 gráficos estadísticos (Chart.js) |
| **Dashboard Lector** | Panel personal con stats propias + últimos préstamos/reservas |
| **Reportes** | Filtros avanzados + exportación a PDF, Excel y CSV |
| **Gestión de usuarios** | Listar, ver detalle y editar usuarios desde la interfaz web |
| **Notificaciones** | Comando de consola para revisar vencimientos |
| **Buscador** | Filtros por título, autor, categoría, estado y fecha |

---

## Tecnologías

- **Backend:** Django 
- **Frontend:** Bootstrap 5.3 + Bootstrap Icons + Chart.js
- **Base de datos:** SQLite (desarrollo) / PostgreSQL (producción)
- **Autenticación:** Django Auth con modelo personalizado
- **PDF:** ReportLab
- **Excel:** openpyxl
- **Servidor estático:** Whitenoise

---

## Instalación local

### 1. Clonar el repositorio

```bash
git clone <URL-del-repositorio>
cd biblioteca-digital
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
SECRET_KEY=django-insecure-cambia-esto-por-una-clave-muy-larga-y-secreta
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email (dejar en consola para desarrollo)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=biblioteca@demo.com
```

### 5. Aplicar migraciones

```bash
python manage.py migrate
```

### 6. Crear superusuario administrador

```bash
python manage.py createsuperuser
```

### 7. Cargar datos de demostración

```bash
python manage.py cargar_datos_demo
```

Esto crea:
- 5 categorías, 7 autores, 10 libros con distintos estados
- Usuario bibliotecario: `admin_bib` / `Admin1234!`
- Usuario lector 1: `lector_juan` / `Lector1234!`
- Usuario lector 2: `lector_sofia` / `Lector1234!`
- Préstamos activos, devueltos, retrasados y reservas

### 8. Ejecutar el servidor

```bash
python manage.py runserver 8001
```

---

## Modelos principales

```
Usuario (accounts)          → AbstractUser + rol, sanciones
Libro (catalogo)            → título, ISBN, autores, categorías, estado
Autor (catalogo)            → nombre, apellido, nacionalidad, foto
Categoria (catalogo)        → nombre, descripción, color
Prestamo (prestamos)        → libro, usuario, fechas, estado, retraso
Reserva (prestamos)         → libro, usuario, fecha expiración, estado
Sancion (prestamos)         → usuario, préstamo, días, activa
```

---

## Rutas principales

| Ruta | Descripción |
|---|---|
| `/accounts/login/` | Inicio de sesión |
| `/accounts/registro/` | Registro de usuario |
| `/accounts/logout/` | Cierre de sesión |
| `/accounts/perfil/` | Perfil del usuario |
| `/accounts/usuarios/` | Lista de usuarios (solo bibliotecario) |
| `/dashboard/` | Panel de control con gráficos |
| `/catalogo/libros/` | Catálogo de libros con filtros |
| `/catalogo/libros/nuevo/` | Crear libro (solo bibliotecario) |
| `/catalogo/autores/` | Lista de autores |
| `/catalogo/categorias/` | Lista de categorías |
| `/prestamos/` | Lista de préstamos |
| `/prestamos/reservas/` | Lista de reservas |
| `/prestamos/sanciones/` | Lista de sanciones |
| `/prestamos/reportes/` | Reportes con filtros |
| `/prestamos/reportes/pdf/` | Exportar PDF |
| `/prestamos/reportes/excel/` | Exportar Excel |
| `/prestamos/reportes/csv/` | Exportar CSV |
| `/admin/` | Panel de administración de Django |

---

## Comandos útiles

```bash
# Verificar el proyecto
python manage.py check

# Crear y aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Cargar datos de prueba
python manage.py cargar_datos_demo

# Verificar vencimientos (simula envío de emails)
python manage.py verificar_vencimientos
python manage.py verificar_vencimientos --dias 7
python manage.py verificar_vencimientos --solo-consola

# Recolectar archivos estáticos (para producción)
python manage.py collectstatic
```

---

## Preparación para despliegue (Render / Railway / PythonAnywhere)

### Variables de entorno en producción (Render)

```env
SECRET_KEY=<clave-secreta-larga-y-aleatoria>
DEBUG=False
ALLOWED_HOSTS=.onrender.com

# Render provee DATABASE_URL automáticamente al conectar un servicio PostgreSQL
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DBNAME
```

---

## Despliegue en Render

### Archivos de despliegue incluidos

| Archivo | Descripción |
|---|---|
| `render.yaml` | Configuración declarativa del servicio (web + base de datos) |
| `build.sh` | Script de construcción: instala deps, collectstatic, migrate |
| `Procfile` | Comando de inicio: `gunicorn config.wsgi:application` |
| `runtime.txt` | Versión de Python: `python-3.11.0` |
| `.env.example` | Plantilla de variables de entorno (copiar como `.env`) |

### Pasos para desplegar en Render

1. **Fork / sube el proyecto a GitHub** (rama `main` o `feature/deploy`).

2. **Crea una cuenta en [render.com](https://render.com)** e inicia sesión.

3. **Opción A — Usando `render.yaml` (recomendado):**
   - Dashboard → New → Blueprint
   - Selecciona el repositorio → Render detecta `render.yaml` automáticamente
   - Revisa las variables de entorno y confirma

4. **Opción B — Manual:**
   - Dashboard → New → Web Service
   - Conecta el repositorio
   - Configura:
     - **Runtime:** Python 3
     - **Build Command:** `./build.sh`
     - **Start Command:** `gunicorn config.wsgi:application`
   - En Environment Variables agrega:
     - `SECRET_KEY` → genera una clave segura
     - `DEBUG` → `False`
     - `ALLOWED_HOSTS` → `.onrender.com`
   - Crea un PostgreSQL: New → PostgreSQL → conecta al Web Service
     - Render inyecta `DATABASE_URL` automáticamente

5. **Primera vez — cargar datos demo** (desde la consola Shell de Render):
   ```bash
   python manage.py cargar_datos_demo
   ```

6. **URL del proyecto:** `https://biblioteca-digital-XXXXX.onrender.com`

### Variables de entorno en el panel de Render

| Variable | Valor en producción |
|---|---|
| `SECRET_KEY` | Generado por Render (`generateValue: true`) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.onrender.com` |
| `DATABASE_URL` | Automático desde PostgreSQL de Render |

> **Nota:** El tier gratuito de Render tiene el servicio web inactivo si no recibe tráfico por 15 min. La primera visita puede tardar ~30 segundos en responder (cold start).

---

## Usuarios de demostración

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin_bib` | `Admin1234!` | Bibliotecario (panel completo) |
| `lector_juan` | `Lector1234!` | Lector (sin sanciones) |
| `lector_sofia` | `Lector1234!` | Lector (con sanción activa — demo) |

```bash
# Crear usuarios demo en producción:
python manage.py cargar_datos_demo
```

---

## Autor

Desarrollado como proyecto académico de gestión de biblioteca digital con Django 6.
