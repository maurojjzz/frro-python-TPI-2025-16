import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, date
# from turtle import pd -> Me dice que genera error
from data.repositories.consumo_repository import ConsumoRepository
from data.repositories.comida_repository import ComidaRepository
import pandas as pds

# Evitar error de tkinter con graficos matplotlib
import matplotlib
matplotlib.use('Agg')


class ConsumoController:

    @staticmethod
    def actualizar_consumo_diario(usuario_id: int, fecha: datetime.date = None):
        if fecha is None:
            fecha = datetime.now().date()

        try:
            totales = ComidaRepository.obtener_totales_dia(usuario_id, fecha)

            consumo_diario = ConsumoRepository.add_update_consumo_diario(
                usuario_id=usuario_id,
                fecha=fecha,
                datos=totales
            )
            return consumo_diario

        except Exception as e:
            print(f"Error al actualizar consumo diario: {str(e)}")
            return None

    @staticmethod
    def actualizar_consumo_semanal(usuario_id: int, fecha_referencia: datetime.date = None):
        if fecha_referencia is None:
            fecha_referencia = datetime.now().date()
        try:
            fecha_inicio = fecha_referencia - \
                timedelta(days=fecha_referencia.weekday())
            fecha_fin = fecha_inicio + timedelta(days=6)

            consumo_semana = ComidaRepository.obtener_consumos_diarios_rango(
                usuario_id=usuario_id,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )

            total_proteinas = sum(c['proteinas'] for c in consumo_semana)
            total_grasas = sum(c['grasas'] for c in consumo_semana)
            total_carbohidratos = sum(c['carbohidratos']for c in consumo_semana)
            total_calorias = sum(c['calorias'] for c in consumo_semana)
            total_colesterol = sum(c['colesterol'] for c in consumo_semana)

            dias_totales = 7

            datos_semanal = {
                "proteinas_total": total_proteinas,
                "grasas_total": total_grasas,
                "carbohidratos_total": total_carbohidratos,
                "calorias_total": total_calorias,
                "colesterol_total": total_colesterol,

                "proteinas_promedio": total_proteinas / dias_totales if dias_totales > 0 else 0,
                "grasas_promedio": total_grasas / dias_totales if dias_totales > 0 else 0,
                "carbohidratos_promedio": total_carbohidratos / dias_totales if dias_totales > 0 else 0,
                "calorias_promedio": total_calorias / dias_totales if dias_totales > 0 else 0,
                "colesterol_promedio": total_colesterol / dias_totales if dias_totales > 0 else 0
            }

            consumo_semanal = ConsumoRepository.add_update_consumo_semanal(
                usuario_id=usuario_id,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                datos=datos_semanal
            )

            return consumo_semanal
        except Exception as e:
            print(f"Error al actualizar consumo semanal: {str(e)}")
            return None

    @staticmethod
    def obtener_consumo_diario(usuario_id: int, fecha: datetime.date):
        try:
            consumo = ConsumoRepository.obtener_consumo_diario(
                usuario_id, fecha)
            if not consumo:
                consumo = ConsumoController.actualizar_consumo_diario(
                    usuario_id, fecha)
            return consumo
        except Exception as e:
            print(f"Error al obtener consumo diario: {str(e)}")
            return None

    @staticmethod
    def obtener_consumo_semanal(usuario_id: int, fecha_inicio: datetime.date):
        try:
            consumo = ConsumoRepository.obtener_consumo_semanal(
                usuario_id, fecha_inicio)
            if not consumo:
                consumo = ConsumoController.actualizar_consumo_semanal(
                    usuario_id, fecha_inicio)
            return consumo
        except Exception as e:
            print(f"Error al obtener consumo semanal: {str(e)}")
            return None

    @staticmethod
    def obtener_semanas_con_datos(usuario_id: int, cantidad_semanas: int = 4):
        semanas = []
        hoy = datetime.now().date()

        for i in range(cantidad_semanas):
            # Retroceder i semanas desde hoy
            fecha_semana = hoy - timedelta(weeks=i)
            consumo_semanal = ConsumoController.obtener_consumo_semanal(
                usuario_id, fecha_semana)

            if consumo_semanal and consumo_semanal.calorias_total > 0:
                semanas.append(consumo_semanal)

        return semanas

    @staticmethod
    def actualizar_ultimas_semanas(usuario_id: int, cantidad_semanas: int = 4):
        semanas_actualizadas = []
        hoy = datetime.now().date()

        for i in range(cantidad_semanas):
            fecha_semana = hoy - timedelta(weeks=i)
            consumo = ConsumoController.actualizar_consumo_semanal(
                usuario_id, fecha_semana)

            if consumo:
                semanas_actualizadas.append(consumo)

        return semanas_actualizadas

    @staticmethod
    def inicializar_consumos_historicos(usuario_id: int):
        from data.database import SessionLocal
        from data.models import Comida
        from sqlalchemy import func

        db = SessionLocal()
        try:
            primera_comida = db.query(Comida).filter(
                Comida.usuario_id == usuario_id
            ).order_by(Comida.fecha_consumo.asc()).first()

            if not primera_comida:
                return []

            fecha_inicio = primera_comida.fecha_consumo
            hoy = datetime.now().date()

            dias_diferencia = (hoy - fecha_inicio).days
            semanas_totales = (dias_diferencia // 7) + 1

            semanas_actualizadas = []
            for i in range(semanas_totales):
                fecha_semana = hoy - timedelta(weeks=i)
                consumo = ConsumoController.actualizar_consumo_semanal(
                    usuario_id, fecha_semana)

                if consumo and consumo.calorias_total > 0:
                    semanas_actualizadas.append(consumo)

            return semanas_actualizadas

        except Exception as e:
            return []
        finally:
            db.close()

    @staticmethod
    def todas_las_comidas(usuario_id: int):
        try:
            comidas = ComidaRepository.obtener_todas_las_comidas(usuario_id)
            return comidas
        except Exception as e:
            print(f"Error al obtener todas las comidas: {str(e)}")
            return []

    @staticmethod
    def obtener_ultimos_consumos_semanales(usuario_id: int, limite: int = 2):
        try:
            return ConsumoRepository.obtener_ultimos_consumos_semanales(usuario_id, limite)
        except Exception as e:
            print(f"Error al obtener últimos consumos semanales: {str(e)}")
            return []

    @staticmethod
    def calculoNutrientesMax(df: pds.DataFrame, comidas_usuario_df: pds.DataFrame):
        comidas_usuario_df['fecha_consumo'] = pds.to_datetime(comidas_usuario_df['fecha_consumo'])

        fecha_inicio = pds.to_datetime(df['fecha_inicio'].iloc[0])
        fecha_fin = pds.to_datetime(df['fecha_fin'].iloc[0])

        comidas_filtradas = comidas_usuario_df[comidas_usuario_df['fecha_consumo'].between(fecha_inicio, fecha_fin, inclusive='both')]

        if comidas_filtradas.empty:
            return {
                "comida_max_calorias": {
                    "nombre": "Sin datos",
                    "calorias": "-",
                    "imagen_url": "",
                    "fecha_consumo": "-"
                },
                "com_max_grasas": {
                    "nombre": "Sin datos",
                    "grasas": "-",
                    "imagen_url": "",
                    "fecha_consumo": "-"
                },
                "com_max_proteinas": {
                    "nombre": "Sin datos",
                    "proteinas": "-",
                    "imagen_url": "",
                    "fecha_consumo": "-"
                }
            }

        comida_max_calorias = comidas_filtradas.loc[[comidas_filtradas["calorias"].idxmax()]]
        com_max_grasas = comidas_filtradas.loc[[comidas_filtradas["grasas"].idxmax()]]
        com_max_proteinas = comidas_filtradas.loc[[comidas_filtradas["proteinas"].idxmax()]]

        return {
            "comida_max_calorias": {
                "nombre": comida_max_calorias["nombre"].values[0],
                "calorias": comida_max_calorias["calorias"].values[0],
                "imagen_url": comida_max_calorias["imagen_url"].values[0],
                "fecha_consumo": comida_max_calorias["fecha_consumo"].values[0].astype(str).split("T")[0]
            },
            "com_max_grasas": {
                "nombre": com_max_grasas["nombre"].values[0],
                "grasas": com_max_grasas["grasas"].values[0],
                "imagen_url": com_max_grasas["imagen_url"].values[0],
                "fecha_consumo": com_max_grasas["fecha_consumo"].values[0].astype(str).split("T")[0]
            },
            "com_max_proteinas": {
                "nombre": com_max_proteinas["nombre"].values[0],
                "proteinas": com_max_proteinas["proteinas"].values[0],
                "imagen_url": com_max_proteinas["imagen_url"].values[0],
                "fecha_consumo": com_max_proteinas["fecha_consumo"].values[0].astype(str).split("T")[0]
            }
        }

# DATOS PARA UNA SOLA FECHA

# Generacion de graficos
    @staticmethod
    def generar_graficos(usuario_id: int, fecha_str: str):
        sns.set_theme(style="darkgrid")  # aplica estilo Seaborn a Matplotlib
        try:
            # Convertimos el string recibido a datetime solo acá
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            return "Formato de fecha inválido"

        # Obtener los datos del consumo para ese día
        consumo = ConsumoController.obtener_consumo_diario(usuario_id, fecha)
        if consumo is None:
            return "No hay datos para esa fecha"

        # Crear DataFrame con los valores
        df = pds.DataFrame([{
            'Proteínas': consumo.proteinas,
            'Grasas': consumo.grasas,
            'Carbohidratos': consumo.carbohidratos,
            'Calorías': consumo.calorias,
            'Colesterol': consumo.colesterol
        }])

        # Generar gráfico de barras
        plt.figure(figsize=(10, 6))
        plt.bar(df.columns, df.iloc[0])
        plt.title(f'Consumo Diario - {fecha}')
        plt.axhline(y=2000, color='r', linestyle='--',
                    label='Objetivo Calórico (2000 kcal)')
        plt.legend()
        plt.ylabel('Cantidad')
        plt.xlabel('Macronutrientes')
        for i, valor in enumerate(df.iloc[0]):
            plt.text(i, valor + 10, str(int(valor)), ha='center')

        plt.tight_layout()

        # Guardar la imagen en static
        ruta_grafico = 'presentation/static/images/graficos/grafico_barras.png'
        plt.savefig(ruta_grafico)
        plt.close()

        # Generar grafico de torta con proteinas, grasas y carbohidratos
        torta_df = df[['Proteínas', 'Grasas', 'Carbohidratos']]
        plt.figure(figsize=(8, 8))
        plt.pie(torta_df.iloc[0], labels=torta_df.columns,
                autopct='%1.1f%%', startangle=140)
        plt.title(f'Consumo Diario - {fecha}')
        plt.axis('equal')

        # Guardar la imagen en static
        ruta_grafico_torta = 'presentation/static/images/graficos/grafico_torta.png'
        plt.savefig(ruta_grafico_torta)
        plt.close()

        # Generar datos para el grafico de linea
        comidas = ComidaRepository.obtener_registro_comidas_dia(
            usuario_id, fecha)
        registros = [{'nombre': c.nombre, 'calorias': c.calorias}
                     for c in comidas]
        linea_df = pds.DataFrame(registros)
        # Generar grafico de lineas de caloria en el dia

        plt.figure(figsize=(10, 6))
        plt.plot(linea_df.index, linea_df['calorias'], marker='o')
        plt.title(f'Consumo de Calorías - {fecha}')
        plt.axhline(y=2000, color='r', linestyle='--',
                    label='Objetivo Calórico (2000 kcal)')
        plt.legend()
        plt.ylabel('Calorías')
        plt.xlabel('Nro de Registro')
        plt.xticks(linea_df.index)
        plt.tight_layout()

        # Guardar la imagen en static
        ruta_grafico_lineas = 'presentation/static/images/graficos/grafico_lineas.png'
        plt.savefig(ruta_grafico_lineas)
        plt.close()

        # Generar grafico de lineas de calorias en la semana
        return {
            "grafico_barras": "grafico_barras.png",
            "grafico_torta": "grafico_torta.png",
            "grafico_lineas": "grafico_lineas.png"
        }

    # Datos para varias fechas

    @staticmethod
    def generar_graficos_semanales(usuario_id: int, fecha_inicio: str, fecha_fin: str):
        sns.set_theme(style="darkgrid")

        try:
            fecha_inicio_dt = datetime.strptime(
                fecha_inicio, "%Y-%m-%d").date()
            fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        except ValueError:
            return "Formato de fecha inválido"

        consumos_semanales = ComidaRepository.obtener_consumos_diarios_rango(
            usuario_id, fecha_inicio_dt, fecha_fin_dt)
        if not consumos_semanales:
            return "No hay datos para el rango de fechas proporcionado"
        df = pds.DataFrame(consumos_semanales).sort_values(by='fecha')

        # Se reindexa el df para completar las fechas faltantes en el rango
        rango_fechas = pds.date_range(fecha_inicio_dt, fecha_fin_dt)
        df = df.set_index('fecha').reindex(
            rango_fechas, fill_value=0).rename_axis('fecha').reset_index()

        # Grafico de barras para calorias diarias en el rango
        plt.figure(figsize=(10, 6))
        plt.bar(df['fecha'], df['calorias'])
        plt.title(f'Consumo Diario de Calorías - {fecha_inicio} a {fecha_fin}')
        plt.axhline(y=2000, color='r', linestyle='--',
                    label='Objetivo Calórico (2000 kcal)')
        plt.legend()
        plt.ylabel('Calorías')
        plt.xlabel('Fecha')
        plt.xticks(rotation=45, ha='right')
        for i, valor in enumerate(df['calorias']):
            plt.text(df['fecha'].iloc[i], valor + 50,
                     str(int(valor)), ha='center')

        plt.tight_layout()
        ruta_grafico = 'presentation/static/images/graficos/grafico_barras_semanal.png'
        plt.savefig(ruta_grafico)
        plt.close()

        # Grafico de torta para consumo semanal
        plt.figure(figsize=(8, 8))
        plt.pie([df['proteinas'].sum(), df['grasas'].sum(), df['carbohidratos'].sum()], labels=[
                'Proteínas', 'Grasas', 'Carbohidratos'], autopct='%1.1f%%', startangle=140)
        plt.title(f'Consumo Semanal - {fecha_inicio} a {fecha_fin}')
        plt.axis('equal')
        ruta_grafico_torta = 'presentation/static/images/graficos/grafico_torta_semanal.png'
        plt.savefig(ruta_grafico_torta)
        plt.close()

        # Grafico de lineas para calorias diarias en el rango
        plt.figure(figsize=(10, 6))
        plt.plot(df['fecha'], df['calorias'], marker='o')
        plt.title(f'Consumo Diario de Calorías - {fecha_inicio} a {fecha_fin}')
        plt.axhline(y=2000, color='r', linestyle='--',
                    label='Objetivo Calórico (2000 kcal)')
        plt.legend()
        plt.ylabel('Calorías')
        plt.xlabel('Fecha')
        plt.xticks(df['fecha'])
        plt.tight_layout()
        ruta_grafico_lineas = 'presentation/static/images/graficos/grafico_lineas_semanal.png'
        plt.savefig(ruta_grafico_lineas)
        plt.close()

        return {
            "grafico_barras": "grafico_barras_semanal.png",
            "grafico_torta": "grafico_torta_semanal.png",
            "grafico_lineas": "grafico_lineas_semanal.png"
        }
