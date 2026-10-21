#!/usr/bin/env bash
# Script de construcción y preparación para despliegue en Vercel
set -o errexit

echo "============================================================"
echo "==> [Vercel Build] 1. Instalando dependencias de Python..."
echo "============================================================"
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "============================================================"
echo "==> [Vercel Build] 2. Recolectando archivos estáticos..."
echo "============================================================"
python3 manage.py collectstatic --no-input --clear

echo "============================================================"
echo "==> [Vercel Build] 3. Aplicando migraciones de base de datos..."
echo "============================================================"
python3 manage.py migrate --no-input

echo "============================================================"
echo "==> [Vercel Build] 4. Verificando superusuario inicial..."
echo "============================================================"
python3 manage.py ensure_superuser || true

echo "============================================================"
echo "==> [Vercel Build] Build completado con éxito."
echo "============================================================"
