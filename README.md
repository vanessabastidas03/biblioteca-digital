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

### Variables de entorno en producción

```env
SECRET_KEY=<clave-secreta-larga-y-aleatoria>
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com

# Base de datos PostgreSQL (Render/Railway proveen DATABASE_URL)
DATABASE_URL=postgresql://...

# Email SMTP real
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-correo@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
DEFAULT_FROM_EMAIL=tu-correo@gmail.com
```

### Archivos de despliegue

- `Procfile` — comando de inicio para Render/Railway (ya incluido)
- `requirements.txt` — dependencias del proyecto (ya incluido)
- `whitenoise` — sirve archivos estáticos sin servidor adicional

### Pasos antes de desplegar

```bash
# 1. Verificar sin errores
python manage.py check --deploy

# 2. Recolectar estáticos
python manage.py collectstatic --no-input

# 3. Aplicar migraciones
python manage.py migrate
```

---

## Autor

Desarrollado como proyecto académico de electiva I por Vanessa Bastidas
