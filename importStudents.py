from database import *
from models import *
import students as studentsApi

schools = [{
    "school_id" : "517",
    "branch_id" : "4733693427"
}]

def findClassId(class_name, classes):
    for classObject in classes:
        if classObject.name == class_name:
            return classObject.class_id

for school in schools:
    classes = session.query(Class).filter(Class.school_branch_id==school["branch_id"])
    studentsList = studentsApi.students(school)
    if studentsList["status"] == "ok":
        print len(studentsList["students"])
        for student in studentsList["students"]:
            try:
                session.merge(Student(
                    student["name"],
                    student["student_id"],
                    student["context_card_id"],
                    findClassId(student["class_name"], classes),
                    student["class_student_id"],
                    student["class_description"],
                    student["status"],
                    student["school_id"],
                    student["branch_id"]
                ))
            except BaseException:
                print "Error"

            try:
                session.commit()
            except BaseException:
                print "Error"