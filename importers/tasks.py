from __future__ import absolute_import

from cel import app

@app.task(name="schools")
def schools():
	from importers import importSchools

	importSchools.importSchools()

@app.task
def classes( school_id, branch_id ):
	from importers import importClasses

	importClasses.importClasses( school_id, branch_id )

@app.task
def groups( school_id, branch_id ):
	from importers import importGroups

	importGroups.importGroups( school_id, branch_id )

@app.task
def students( school_id, branch_id ):
	from importers import importStudents

	importStudents.importStudents( school_id, branch_id )

@app.task
def ressources( school_id, branch_id ):
	from importers import importRessources

	importRessources.importRessources( school_id, branch_id )

@app.task
def rooms( school_id, branch_id ):
	from importers import importRooms

	importRooms.importRooms( school_id, branch_id )

@app.task
def teachers( school_id, branch_id ):
	from importers import importTeachers

	importTeachers.importTeachers( school_id, branch_id )

@app.task
def teams( school_id, branch_id ):
	from importers import importTeams

	importTeams.importTeams( school_id, branch_id )