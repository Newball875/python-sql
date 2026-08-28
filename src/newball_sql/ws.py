from .config import *

from abc import abstractmethod
from typing import Self, List
import os

from sqlalchemy.orm import DeclarativeBase, Mapped, Session, sessionmaker, mapped_column
from sqlalchemy import Integer, create_engine, select, event, text
from sqlalchemy.dialects.postgresql import insert as postgres_insert

### Classe des données ###

class Base(DeclarativeBase):
	pass

class WS(Base):
	__abstract__ = True

	id: Mapped[int] = mapped_column(Integer, primary_key=True)

	@classmethod
	def afficher(cls, session:Session) -> List[Self]:
		return session.scalars(select(cls).order_by("id"))
	
	@classmethod
	def recupId(cls, session:Session, id:int) -> Self | None:
		return session.get(cls, id)
	
	@property
	def table(self) -> str:
		return self.__tablename__
	
	@staticmethod
	@abstractmethod
	def recupId(session:Session, id:int):
		pass

class Migrations(Base):
	"""
	Classe pour gérer les migrations via Python
	"""
	__tablename__ = "migrations"

	version: Mapped[int] = mapped_column(Integer, primary_key=True)

	@classmethod
	def afficher(cls, session:Session) -> List[Self]:
		return session.scalars(select(cls).order_by("version"))
	
	@classmethod
	def recupId(cls, session:Session, id:int) -> Self | None:
		return session.get(cls, id)
	
	@classmethod
	def recupLast(cls, session:Session) -> Self | None:
		result = session.scalars(select(cls).order_by(cls.version.desc()))
		if result:
			return result.first()
		return None
	
	@classmethod
	def creer(cls, session:Session, numero:int) -> Self:
		test = cls.recupId(session, numero)
		if test:
			return test
		migrations = Migrations(version = numero)
		session.add(migrations)
		return migrations
	
	@property
	def table(self) -> str:
		return self.__tablename__
	
	def __repr__(self):
		return f"Migration n°{self.version}"

### Fonctions ###

def creerSession() -> Session:
	"""
	Crée une session PostgreSQL avec les infos des fichiers .env
	"""

	user = os.getenv("DB_USER")
	password = os.getenv("DB_PASSWORD")
	host = os.getenv("DB_HOST")
	port = os.getenv("DB_PORT")
	db = os.getenv("DB_NAME")
	engine = create_engine("postgresql://" + user + ":" + password + "@" + host + "/" + db)
	Session = sessionmaker(engine)
	return Session()

def runMigrations(session:Session, sql:str, numero:int) -> None:
	"""
	Exécute la migration d'un fichier
	"""
	try:
		session.execute(text(sql))
		migrations = Migrations.creer(session, numero)
		session.commit()
		print(f"{migrations} réussie")
	except Exception as e:
		session.rollback()
		print(f"Échec de la migration {numero}")
		raise e

def finJob(session:Session) -> None:
	"""
	Envoie toutes les données de la session à la base de données
	"""

	session.flush()
	session.commit()


