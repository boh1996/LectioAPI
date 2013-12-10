schema = {
    'id' : {
        "type" : "integer",
    },
    "name" : {
        "type" : "string",
        "empty" : False,
        "minlength" : 1
    },
    "student_id" : {
        "type" : "integer",
        "empty" : False,
        "minlength" : 1,
        "unique" : True
    },
    "context_card_id" : {
        "type" : "integer",
        "empty" : False,
        "minlength" : 1,
        "unique" : True
    },
    "class_id" : {
        "type" : "integer",
        "empty" : False,
        "minlength" : 1
    },
    "class_student_id" : {
        "type" : "string",
        "empty" : False,
        "minlength" : 1,
    },
    "class_description" : {
        "type" : "string"
    },
    "status" : {
        "type" : "string"
    },
    "school_id" : {
        "type" : "integer"
    },
    "school_branch_id" : {
        "type" : "integer"
    }
}