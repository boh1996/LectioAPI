import sqlalchemy
from sqlalchemy import Table, MetaData, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import mapper
from sqlalchemy.ext.declarative import declarative_base
import database
from datetime import *
from time import mktime
from sqlalchemy.schema import UniqueConstraint

Base = declarative_base()

class School(Base):
    __tablename__ = "schools"
    __table_args__ = (UniqueConstraint("school_id", "school_branch_id", name='_school_identification'),)
    id = Column(Integer(11), primary_key=True)
    name = Column(String(255))
    school_id = Column(Integer(11))
    school_branch_id = Column(String(255), unique=True, nullable=False)

    def __init__(self, name, school_id, branch_id):
        self.name = name
        self.school_id = school_id
        self.school_branch_id = branch_id

class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer(11), primary_key=True)
    name = Column(String(255))
    school_id = Column(Integer(11))
    school_branch_id = Column(String(255), ForeignKey("schools.school_branch_id"))
    class_id = Column(String(255), unique=True)

    def __init__(self, name, school_id, branch_id, class_id):
        self.name = name
        self.school_id = school_id
        self.school_branch_id = branch_id
        self.class_id = class_id

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer(11), primary_key=True)
    name = Column(String(255))
    student_id = Column(String(255), unique=True, nullable=False)
    context_card_id = Column(String(11))
    class_id = Column(String(255), ForeignKey("classes.class_id"))
    class_student_id = Column(String(255))
    class_description = Column(String(255))
    status = Column(String(200))
    school_id = Column(Integer(11))
    school_branch_id = Column(String(255), ForeignKey("schools.school_branch_id"))

    def __init__(self, name, student_id, context_card_id, student_class, class_student_id, class_description, status, school_id, branch_id):
        self.name = name
        self.context_card_id = context_card_id
        self.student_id = student_id
        self.class_id = student_class
        self.class_student_id = class_student_id
        self.class_description = class_description
        self.status = status
        self.school_id = school_id
        self.school_branch_id = branch_id

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer(11), primary_key=True)
    name = Column(String(255))
    number = Column(String(255))
    room_id = Column(String(255), unique=True)
    school_id = Column(String(255))
    school_branch_id = Column(String(255), ForeignKey("schools.school_branch_id"))

    def __init__(self, name, number, room_id, school_id, branch_id):
        self.name = name
        self.number = number
        self.room_id = room_id
        self.school_id = school_id
        self.school_branch_id = branch_id

class Ressource(Base):
    __tablename__ = "ressources"
    id = Column(Integer(11), primary_key=True)
    name = Column(String(255))
    ressource_id = Column(String(255), unique=True)
    title = Column(String(255))
    school_id = Column(String(255))
    school_branch_id = Column(String(255), ForeignKey("schools.school_branch_id"))

    def __init__(self, name, ressource_id, title, school_id, branch_id):
        self.name = name
        self.ressource_id = ressource_id
        self.title = title
        self.school_id = school_id
        self.school_branch_id = branch_id


class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer(11), primary_key=True)
    week = Column(String(3))
    group = Column(String(255))
    title = Column(String(255))
    team_context_card_id = Column(String(255))# ForeignKey to teams.team_context_card_id
    exercise_id = Column(String(255), unique=True)
    link = Column(String)
    date = Column(String(255))
    hours = Column(String(255))
    status = Column(String(255))
    leave = Column(String(5))
    waiting_for = Column(String(50))
    note = Column(Text)
    grade = Column(String(50))
    student_note = Column(Text)

    def __init__(self,
         week,
         group,
         title,
         team_context_id,
         exercise_id,
         link,
         date,
         hours,
         status,
         leave,
         waiting_for,
         note = "",
         grade = "",
         student_note = ""
    ):
        self.week = week
        self.group = group
        self.title = title
        self.team_context_card_id = team_context_id
        self.exercise_id = exercise_id
        self.link = link
        self.date = str(mktime(date.timetuple()))[:-2]
        self.hours = hours
        self.status = status
        self.leave = leave
        self.waiting_for = waiting_for
        self.note = note
        self.grade = grade
        self.student_note = student_note


class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer(11), primary_key=True)
    name = Column(String(255))
    context_card_id = Column(String(11), unique=True)
    initial = Column(String(20))
    teacher_id = Column(String(20), unique=True)
    school_id = Column(String(255))
    school_branch_id = Column(String(255), ForeignKey("schools.school_branch_id"))

    def __init__(self, name, context_card_id, initial, teacher_id, school_id, branch_id):
        self.name = name
        self.context_card_id = context_card_id
        self.initial = initial
        self.teacher_id = teacher_id
        self.school_id = school_id
        self.school_branch_id = branch_id

Base.metadata.create_all(database.engine)