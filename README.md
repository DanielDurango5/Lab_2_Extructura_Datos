# Lab_2_Extructura_Datos

Laboratorio 2 - Hashing Dinamico vs Busqueda Secuencial.

Implementacion en Python de los puntos funcionales del laboratorio:

- registro de usuarios (nombre, cedula, correo),
- validacion de cedulas duplicadas,
- busqueda con hashing extendible,
- busqueda secuencial,
- comparacion de tiempos en milisegundos,
- carga masiva de datos de prueba.

## Estructura

- src/main/python/org/example/main.py: codigo principal del laboratorio.
- run.ps1: script rapido para ejecutar en PowerShell.

## Requisitos

- Python 3.10 o superior.
- No requiere librerias externas.

## Ejecucion

Opcion 1 (recomendada en Windows):

```
run.bat
```

Opcion 2 (PowerShell):

```
./run.ps1
```

Opcion 3 (directo con Python):

```
python ./src/main/python/org/example/main.py
```

## Menu de la aplicacion

1. Registrar usuario
2. Buscar usuario por cedula
3. Cargar datos de prueba
4. Ver resumen de estructura
5. Salir

## Observacion

La aplicacion esta hecha por consola y no utiliza base de datos externa, de acuerdo con el enunciado del laboratorio.
