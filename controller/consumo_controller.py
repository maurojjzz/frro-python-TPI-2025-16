from datetime import datetime, timedelta
from turtle import pd
from data.repositories.consumo_repository import ConsumoRepository
from data.repositories.comida_repository import ComidaRepository
import pandas as pds

#Evitar error de tkinter con graficos matplotlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns






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
            fecha_inicio = fecha_referencia - timedelta(days=fecha_referencia.weekday())
            fecha_fin = fecha_inicio + timedelta(days=6)

            consumo_semana = ComidaRepository.obtener_consumos_diarios_rango(
                usuario_id=usuario_id,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )

            total_proteinas = sum(c['proteinas'] for c in consumo_semana)
            total_grasas = sum(c['grasas'] for c in consumo_semana)
            total_carbohidratos = sum(c['carbohidratos']
                                      for c in consumo_semana)
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
    def obtener_consumo_diario(usuario_id:int, fecha:datetime.date):
        try:
            consumo = ConsumoRepository.obtener_consumo_diario(usuario_id, fecha)
            if not consumo:
                consumo= ConsumoController.actualizar_consumo_diario(usuario_id, fecha)
            return consumo
        except Exception as e:
            print(f"Error al obtener consumo diario: {str(e)}")
            return None
        
    @staticmethod
    def obtener_consumo_semanal(usuario_id:int, fecha_inicio:datetime.date):
        try:
            consumo = ConsumoRepository.obtener_consumo_semanal(usuario_id, fecha_inicio)
            if not consumo:
                consumo= ConsumoController.actualizar_consumo_semanal(usuario_id, fecha_inicio)
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
            consumo_semanal = ConsumoController.obtener_consumo_semanal(usuario_id, fecha_semana)
            
            if consumo_semanal and consumo_semanal.calorias_total > 0:
                semanas.append(consumo_semanal)
        
        return semanas
    
    @staticmethod
    def actualizar_ultimas_semanas(usuario_id: int, cantidad_semanas: int = 4):
        semanas_actualizadas = []
        hoy = datetime.now().date()
        
        for i in range(cantidad_semanas):
            fecha_semana = hoy - timedelta(weeks=i)
            consumo = ConsumoController.actualizar_consumo_semanal(usuario_id, fecha_semana)

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
                consumo = ConsumoController.actualizar_consumo_semanal(usuario_id, fecha_semana)
                
                if consumo and consumo.calorias_total > 0:
                    semanas_actualizadas.append(consumo)
            
            return semanas_actualizadas
            
        except Exception as e:
            return []
        finally:
            db.close()

#Generacion de graficos
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
        plt.axhline(y=2000, color='r', linestyle='--', label='Objetivo Calórico (2000 kcal)')
        plt.legend()
        plt.ylabel('Cantidad')
        plt.xlabel('Macronutrientes')
        plt.tight_layout()
        
        # Guardar la imagen en static
        ruta_grafico = 'presentation/static/images/graficos/grafico_barras.png'
        plt.savefig(ruta_grafico)
        plt.close()

        # Generar grafico de torta con proteinas, grasas y carbohidratos
        torta_df = df[['Proteínas', 'Grasas', 'Carbohidratos']]
        plt.figure(figsize=(8, 8))
        plt.pie(torta_df.iloc[0], labels=torta_df.columns, autopct='%1.1f%%', startangle=140)
        plt.title(f'Consumo Diario - {fecha}')
        plt.axis('equal')

        # Guardar la imagen en static
        ruta_grafico_torta = 'presentation/static/images/graficos/grafico_torta.png'
        plt.savefig(ruta_grafico_torta)
        plt.close()

        #Generar grafico de lineas de calorias en la semana
        return "Gráfico generado correctamente"