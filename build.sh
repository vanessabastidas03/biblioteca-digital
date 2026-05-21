#!/usr/bin/env bash
# build.sh — Script de construcción para Render
# Se ejecuta automáticamente en cada despliegue.
set -o errexit

echo "==> Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "==> Aplicando migraciones..."
python manage.py migrate

echo "==> Build completado."
