from tasks import schools
from cel import app
print app.tasks.keys()

schools.delay(4,4)