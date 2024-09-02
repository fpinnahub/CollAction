from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Witness(Base):
    __tablename__ = 'witnesses'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    text = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id'))  # Colonna per la chiave esterna
    owner = relationship("User", back_populates="witnesses")


class Collation(Base):
    __tablename__ = "collations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    html_table = Column(Text)  # here the HTML's 'table
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="collations")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # Relationship with other tables
    collations = relationship("Collation", back_populates="owner")
    witnesses = relationship("Witness", back_populates="owner")
