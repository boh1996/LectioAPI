import sqlalchemy
from sqlalchemy import Table, MetaData, Column, ForeignKey, Integer, String
from sqlalchemy.orm import mapper
from sqlalchemy.ext.declarative import declarative_base
import database
from sqlalchemy.schema import UniqueConstraint

Base = declarative_base()

class School(Base):
    __tablename__ = "schools"
    __table_args__ = (UniqueConstraint("school_id", "school_branch_id", name='_school_identification'),)
    id = Column(Integer(11), primary_key=True)
    name = Column(String(255))
    school_id = Column(Integer(11))
    school_branch_id = Column(String(255))

    def __init__(self, name, school_id, branch_id):
        self.name = name
        self.school_id = school_id
        self.school_branch_id = branch_id

class User(Base):
    __tablename__ = "users"
    id = Column(Integer(11), primary_key=True)
    name = Column(String(255))
    lectio_id = Column(String(255))
    username = Column(String(255))
    password = Column(String(255))

    def __init__(self, name, lectio_id, username, password):
        self.name = name
        self.lectio_id = lectio_id
        self.username = username
        self.password = password

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer(11), primary_key=True)
    name = Column(String(255))
    student_id = Column(Integer(11), unique=True)

Base.metadata.create_all(database.engine)