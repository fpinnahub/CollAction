from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Witness(Base):
    __tablename__ = 'witnesses'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    text = Column(String)


class Collation(Base):
    __tablename__ = "collations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    html_table = Column(Text)  # here the HTML's 'table
