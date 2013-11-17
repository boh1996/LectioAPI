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
    context_card_id = Column(String(11))
    student_class = Column(String(11))
    class_student_id = Column(Integer(11))
    class_description = Column(String(255))
    status = Column(String(200))
    school_id = Column(Integer(11), ForeignKey("schools.school_id"))

    def __init__(self, name, student_id, context_card_id, student_class, class_student_id, class_description, status, school_id):
        self.name = name
        self.context_card_id = context_card_id
        self.student_id = student_id
        self.student_class = student_class
        self.class_student_id = class_student_id
        self.class_description = class_description
        self.status = status
        self.school_id = school_id

Base.metadata.create_all(database.engine)