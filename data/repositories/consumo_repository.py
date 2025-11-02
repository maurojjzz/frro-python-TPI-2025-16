from sqlalchemy.orm import Session
from data.database import SessionLocal
from data.models import ConsumoDiario, ConsumoSemanal
from datetime import datetime, date
from typing import Optional


class ConsumoRepository:

    @staticmethod
    def obtener_consumo_diario(usuario_id: int, fecha: date) -> Optional[ConsumoDiario]:
        db = SessionLocal()
        try:
            return db.query(ConsumoDiario).filter(
                ConsumoDiario.usuario_id == usuario_id,
                ConsumoDiario.fecha == fecha
            ).first()
        finally:
            db.close()


    @staticmethod
    def add_update_consumo_diario(usuario_id:int, fecha:date, datos:dict) -> ConsumoDiario:
        db = SessionLocal()
        try:
            consumo = db.query(ConsumoDiario).filter(
                ConsumoDiario.usuario_id == usuario_id,
                ConsumoDiario.fecha == fecha
            ).first()
            
            if consumo:
                for key, value in datos.items():
                    setattr(consumo, key, value)
            else:
                consumo = ConsumoDiario(
                    usuario_id= usuario_id,
                    fecha=fecha,
                    **datos
                )
                db.add(consumo)
                
            db.commit()
            db.refresh(consumo)
            return consumo
        except Exception as e:
            db.rollback()
            print(e)
        finally:
            db.close()
            
            
            
    @staticmethod
    def obtener_consumo_semanal(usuario_id:int, fecha_inicio:date) -> Optional[ConsumoSemanal]:
        db=SessionLocal()
        
        try:
            return db.query(ConsumoSemanal).filter(
                ConsumoSemanal.usuario_id == usuario_id,
                ConsumoSemanal.fecha_inicio == fecha_inicio,
            ).first()
        finally:
            db.close()
            
    @staticmethod
    def add_update_consumo_semanal(usuario_id:int, fecha_inicio:date, fecha_fin:date, datos:dict) -> ConsumoSemanal:
        db = SessionLocal()
        try:
            consumo = db.query(ConsumoSemanal).filter(
                ConsumoSemanal.usuario_id == usuario_id,
                ConsumoSemanal.fecha_inicio == fecha_inicio
            ).first()
            
            if consumo:
                for key, value in datos.items():
                    setattr(consumo, key, value)
            else:
                consumo = ConsumoSemanal(
                    usuario_id= usuario_id,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    **datos
                )
                db.add(consumo)
                
            db.commit()
            db.refresh(consumo)
            return consumo
        except Exception as e:
            db.rollback()
            print(e)
        finally:
            db.close()

    @staticmethod
    def obtener_ultimos_consumos_semanales(usuario_id: int, limite: int = 2):
        db = SessionLocal()
        try:
            return (
                db.query(ConsumoSemanal)
                .filter(ConsumoSemanal.usuario_id == usuario_id)
                .order_by(ConsumoSemanal.fecha_inicio.desc())
                .limit(limite)
                .all()
            )
        finally:
            db.close()