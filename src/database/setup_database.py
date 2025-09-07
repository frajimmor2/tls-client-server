import os
from dotenv import load_dotenv
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from sqlalchemy import Date, create_engine, Column, Integer, String, LargeBinary, ForeignKey

load_dotenv()

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(LargeBinary, nullable=False)

class UserMessage(Base):
    __tablename__ = 'user_messages'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)
    date = Column(Date, primary_key=True, nullable=False)
    cont = Column(Integer, nullable=False)
    
def database_setup():
    DATABASE_URL = f"mysql+pymysql://{os.getenv('MARIADB_USER')}:{os.getenv('MARIADB_PASSWORD')}@{os.getenv('MARIADB_HOSTNAME')}:{os.getenv('MARIADB_PORT')}/{os.getenv('MARIADB_DATABASE')}"
    engine = create_engine(DATABASE_URL)

    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Session = scoped_session(session_factory)
    # Crear la tabla en la base de datos
    Base.metadata.create_all(bind=engine)
    
    return Session