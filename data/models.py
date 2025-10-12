from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime, timedelta, timezone  

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    contrasena = Column(Text, nullable=False)
    comidas = relationship("Comida", back_populates="usuario")
    
    
class Comida(Base):
    __tablename__ = "comidas"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=False)
    calorias = Column(Float, nullable=False)
    grasas = Column(Float, nullable=False)
    proteinas = Column(Float, nullable=False)   
    carbohidratos = Column(Float, nullable=False)
    colesterol = Column(Float, nullable=False)
    fecha_consumo = Column(Date, nullable=False)
    imagen_url = Column(String(255), nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    usuario = relationship("Usuario", back_populates="comidas")
    
class ConsumoDiario(Base):
    __tablename__ = "consumos_diarios"
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False, default=datetime.now(timezone.utc).date())
    proteinas = Column(Float, default=0)
    grasas = Column(Float, default=0)
    calorias = Column(Float, default=0)
    carbohidratos = Column(Float, default=0)
    colesterol = Column(Float, default=0)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    usuario = relationship("Usuario")

    __table_args__ = (UniqueConstraint('usuario_id', 'fecha', name='unique_consumo_diario'),)


class ConsumoSemanal(Base):
    __tablename__ = "consumos_semanales"
    id = Column(Integer, primary_key=True, index=True)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False) 
    
    proteinas_promedio = Column(Float, default=0)
    grasas_promedio = Column(Float, default=0)
    carbohidratos_promedio = Column(Float, default=0)
    calorias_promedio = Column(Float, default=0)
    colesterol_promedio = Column(Float, default=0)
    
    proteinas_total = Column(Float, default=0)
    grasas_total = Column(Float, default=0)
    calorias_total = Column(Float, default=0)
    carbohidratos_total = Column(Float, default=0)
    colesterol_total = Column(Float, default=0)

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("Usuario")

