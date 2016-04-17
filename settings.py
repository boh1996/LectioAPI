SERVER_NAME = '127.0.0.1:4000'
DOMAIN = {
	"public_persons" : {
		"datasource" : {
			"source" : "persons",
			"projection" : {
				"name" : 1,
				"status" : 1,
				"_id" : 1,
				"terms" : 1,
				"branch_id" : 1,
				"school_id" : 1,
				"picture_id" : 1,
				"student_id" : 1,
				"context_cards" : 1,
				"type" : 1,
				"teacher_id" : 1,
				"_updated" : 1,
				"_created" : 1
			}
		}
	},
	"schools" : {
		"datasource" : {
			"source" : "schools"
		}
	},
	"xprs_subjects" : {
		"datasource" : {
			"source" : "xprs_subjects"
		}
	},
	"subjects" : {
		"datasource" : {
			"source" : "subjects"
		}
	},
	"rooms" : {
		"datasource" : {
			"source" : "rooms"
		}
	},
	"ressources" : {
		"datasource" : {
			"source" : "ressources"
		}
	},
	"notices" : {
		"datasource" : {
			"source" : "notices"
		}
	},
	"books" : {
		"datasource" : {
			"source" : "books"
		}
	},
	"classes" : {
		"datasource" : {
			"source" : "classes"
		},
	},
	"field_of_studies" : {
		"datasource" : {
			"source" : "field_of_studies"
		}
	},
	"school_subjects" : {
		"datasource" : {
			"source" : "school_subjects"
		}
	},
	"team_elements" : {
		"datasource" : {
			"source" : "team_elements"
		}
	},
	"teams" : {
		"datasource" : {
			"source" : "teams"
		},
		"schema" : {
			"team_elements" : {
				'type' : "list",
				"_id" : {
					"type" : "objectid",
					'data_relation': {
		                 'resource': 'team_elements',
		                 'field': '_id',
		                 'embeddable': True
		             },
				}
             }
		}
	},

	# Auth Control
	"phases" : {
		"datasource" : {
			"source" : "phases"
		}
	},
	"events" : {
		"datasource" : {
			"source" : "events"
		}
	},
	"persons" : {
		"datasource" : {
			"source" : "persons"
		}
	},
	"information" : {
		"datasource" : {
			"source" : "information"
		}
	},
	"documents" : {
		"datasource" : {
			"source" : "documents"
		}
	}
}

# Let's just use the local mongod instance. Edit as needed.

# Please note that MONGO_HOST and MONGO_PORT could very well be left
# out as they already default to a bare bones local 'mongod' instance.
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_USERNAME = ''
MONGO_PASSWORD = ''
MONGO_DBNAME = 'lectio'

# Enable reads (GET), inserts (POST) and DELETE for resources/collections
# (if you omit this line, the API will default to ['GET'] and provide
# read-only access to the endpoint).
RESOURCE_METHODS = ['GET']

# Enable reads (GET), edits (PATCH), replacements (PUT) and deletes of
# individual items  (defaults to read-only item access).
ITEM_METHODS = ['GET']