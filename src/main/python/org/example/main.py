from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter_ns
import random


@dataclass(frozen=True)
class Usuario:
    nombre: str
    cedula: str
    correo: str


class CedulaDuplicadaError(ValueError):
    pass


class Bucket:
    def __init__(self, local_depth: int, capacidad: int) -> None:
        self.local_depth = local_depth
        self.capacidad = capacidad
        self.registros: dict[str, Usuario] = {}

    def esta_lleno(self) -> bool:
        return len(self.registros) >= self.capacidad


class HashingExtendible:
    def __init__(self, capacidad_bucket: int = 4) -> None:
        if capacidad_bucket < 1:
            raise ValueError("La capacidad del bucket debe ser >= 1")

        self.capacidad_bucket = capacidad_bucket
        self.global_depth = 1
        self.directorio: list[Bucket] = [
            Bucket(local_depth=1, capacidad=capacidad_bucket),
            Bucket(local_depth=1, capacidad=capacidad_bucket),
        ]
        self.total_registros = 0

    def _hash_cedula(self, cedula: str) -> int:
        if cedula.isdigit():
            return int(cedula)

        # FNV-1a para llaves no numericas.
        hash_value = 2166136261
        for ch in cedula:
            hash_value ^= ord(ch)
            hash_value = (hash_value * 16777619) & 0xFFFFFFFF
        return hash_value

    def _indice_directorio(self, cedula: str) -> int:
        mascara = (1 << self.global_depth) - 1
        return self._hash_cedula(cedula) & mascara

    def _duplicar_directorio(self) -> None:
        self.directorio.extend(self.directorio.copy())
        self.global_depth += 1

    def _dividir_bucket(self, indice: int) -> None:
        bucket_objetivo = self.directorio[indice]
        depth_anterior = bucket_objetivo.local_depth

        if depth_anterior == self.global_depth:
            self._duplicar_directorio()

        bucket_0 = Bucket(local_depth=depth_anterior + 1, capacidad=self.capacidad_bucket)
        bucket_1 = Bucket(local_depth=depth_anterior + 1, capacidad=self.capacidad_bucket)

        for cedula, usuario in bucket_objetivo.registros.items():
            bit_reparto = (self._hash_cedula(cedula) >> depth_anterior) & 1
            if bit_reparto == 0:
                bucket_0.registros[cedula] = usuario
            else:
                bucket_1.registros[cedula] = usuario

        for i, bucket in enumerate(self.directorio):
            if bucket is bucket_objetivo:
                bit_reparto = (i >> depth_anterior) & 1
                self.directorio[i] = bucket_1 if bit_reparto == 1 else bucket_0

    def buscar(self, cedula: str) -> Usuario | None:
        indice = self._indice_directorio(cedula)
        return self.directorio[indice].registros.get(cedula)

    def insertar(self, usuario: Usuario) -> None:
        if self.buscar(usuario.cedula) is not None:
            raise CedulaDuplicadaError(f"La cedula {usuario.cedula} ya existe")

        while True:
            indice = self._indice_directorio(usuario.cedula)
            bucket = self.directorio[indice]

            if not bucket.esta_lleno():
                bucket.registros[usuario.cedula] = usuario
                self.total_registros += 1
                return

            self._dividir_bucket(indice)

    def cantidad_buckets_unicos(self) -> int:
        return len({id(bucket) for bucket in self.directorio})


class BusquedaSecuencial:
    def __init__(self) -> None:
        self.registros: list[Usuario] = []
        self._cedulas_registradas: set[str] = set()

    def insertar(self, usuario: Usuario) -> None:
        if usuario.cedula in self._cedulas_registradas:
            raise CedulaDuplicadaError(f"La cedula {usuario.cedula} ya existe")
        self.registros.append(usuario)
        self._cedulas_registradas.add(usuario.cedula)

    def buscar(self, cedula: str) -> Usuario | None:
        for usuario in self.registros:
            if usuario.cedula == cedula:
                return usuario
        return None

    def total(self) -> int:
        return len(self.registros)


class LaboratorioHashingApp:
    def __init__(self, capacidad_bucket: int = 4) -> None:
        self.hashing = HashingExtendible(capacidad_bucket=capacidad_bucket)
        self.secuencial = BusquedaSecuencial()

    def registrar_usuario(self, nombre: str, cedula: str, correo: str) -> None:
        nombre = nombre.strip()
        cedula = cedula.strip()
        correo = correo.strip()

        if not nombre or not cedula or not correo:
            raise ValueError("Nombre, cedula y correo son obligatorios")
        if "@" not in correo:
            raise ValueError("Correo invalido")

        usuario = Usuario(nombre=nombre, cedula=cedula, correo=correo)
        self.hashing.insertar(usuario)
        self.secuencial.insertar(usuario)

    def buscar_usuario_con_tiempos(self, cedula: str) -> tuple[Usuario | None, float, float]:
        cedula = cedula.strip()

        inicio_hash = perf_counter_ns()
        usuario_hash = self.hashing.buscar(cedula)
        tiempo_hash_ms = (perf_counter_ns() - inicio_hash) / 1_000_000

        inicio_seq = perf_counter_ns()
        usuario_seq = self.secuencial.buscar(cedula)
        tiempo_seq_ms = (perf_counter_ns() - inicio_seq) / 1_000_000

        # Si uno encuentra y otro no, se prioriza el encontrado para mostrar datos.
        usuario = usuario_hash if usuario_hash is not None else usuario_seq
        return usuario, tiempo_hash_ms, tiempo_seq_ms

    def cargar_datos_prueba(self, cantidad: int, semilla: int = 42) -> int:
        if cantidad < 1:
            raise ValueError("La cantidad debe ser mayor a 0")

        random.seed(semilla)
        agregados = 0

        while agregados < cantidad:
            cedula = str(random.randint(10_000_000, 99_999_999))
            if self.hashing.buscar(cedula) is not None:
                continue

            indice = self.secuencial.total() + 1
            nombre = f"Usuario{indice}"
            correo = f"usuario{cedula}@correo.com"
            self.registrar_usuario(nombre=nombre, cedula=cedula, correo=correo)
            agregados += 1

        return agregados

    def imprimir_resumen(self) -> None:
        print("\nResumen del sistema")
        print(f"- Registros: {self.secuencial.total()}")
        print(f"- Global depth: {self.hashing.global_depth}")
        print(f"- Buckets unicos: {self.hashing.cantidad_buckets_unicos()}")
        print(f"- Tamano del directorio: {len(self.hashing.directorio)}")


def mostrar_menu() -> None:
    print("\n===== Laboratorio 2: Hashing Extendible =====")
    print("1. Registrar usuario")
    print("2. Buscar usuario por cedula")
    print("3. Cargar datos de prueba")
    print("4. Ver resumen de estructura")
    print("5. Salir")


def main() -> None:
    app = LaboratorioHashingApp(capacidad_bucket=4)

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opcion: ").strip()

        if opcion == "1":
            nombre = input("Nombre: ")
            cedula = input("Cedula: ")
            correo = input("Correo: ")
            try:
                app.registrar_usuario(nombre=nombre, cedula=cedula, correo=correo)
                print("Usuario registrado correctamente.")
            except (ValueError, CedulaDuplicadaError) as error:
                print(f"Error: {error}")

        elif opcion == "2":
            cedula = input("Cedula a buscar: ")
            usuario, tiempo_hash_ms, tiempo_seq_ms = app.buscar_usuario_con_tiempos(cedula)

            if usuario is None:
                print("Usuario no encontrado.")
            else:
                print("Usuario encontrado:")
                print(f"Nombre: {usuario.nombre}")
                print(f"CC: {usuario.cedula}")
                print(f"Correo: {usuario.correo}")

            print(f"Tiempo busqueda (Hashing): {tiempo_hash_ms:.6f} ms")
            print(f"Tiempo busqueda (Secuencial): {tiempo_seq_ms:.6f} ms")

        elif opcion == "3":
            cantidad_str = input("Cantidad de usuarios de prueba: ").strip()
            try:
                cantidad = int(cantidad_str)
                inicio = perf_counter_ns()
                agregados = app.cargar_datos_prueba(cantidad)
                tiempo_carga_ms = (perf_counter_ns() - inicio) / 1_000_000
                print(
                    f"Se cargaron {agregados} usuarios de prueba en {tiempo_carga_ms:.3f} ms."
                )
            except ValueError as error:
                print(f"Error: {error}")

        elif opcion == "4":
            app.imprimir_resumen()

        elif opcion == "5":
            print("Saliendo del programa...")
            break

        else:
            print("Opcion invalida. Intente nuevamente.")


if __name__ == "__main__":
    main()