from database import *
from models import *
import classes as classesApi

schools = [{
    "school_id" : "517",
    "branch_id" : "4733693427"
}]

for school in schools:
    classsList = classesApi.classes(school)

    if classsList["status"] == "ok":
        for classObject in classsList["classes"]:
            session.merge(Class(
                classObject["name"],
                classObject["school_id"],
                classObject["branch_id"],
                classObject["class_id"],
            ))

            try:
                session.commit()
            except BaseException:
                pass