from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from .database import Base

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
