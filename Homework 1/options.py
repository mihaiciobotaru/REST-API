OPTIONS = {
        "GET": {
            "/users": {
                "required_params": [],
                "result": "All the users from the database"
            },
            "/users/<id>": {
                "required_params": ["id - INTEGER"],
                "result": "The user with the given id"
            },
            "/downloads": {
                "required_params": [],
                "result": "All the downloads from the database"
            },
            "/downloads/<id>": {
                "required_params": ["id - INTEGER"],
                "result": "The download with the given id"
            }
        },
        "POST": {
            "/users": {
                "required_params": ["first_name - STRING", "last_name - STRING", "age - INTEGER", "country - STRING"],
                "result": "The created user id"
            },
            "/downloads": {
                "required_params": ["user_id - INTEGER", "file_name - STRING"],
                "result": "The created download id"
            }
        },
        "PUT": {
            "/users/downloads": {
                "required_params": ["user_id - INTEGER", "downloads - INTEGER"],
                "result": "The updated user id"
            },
            "/users/subscription": {
                "required_params": ["user_id - INTEGER", "subscription - STRING"],
                "result": "The updated user id"
            },
            "/users/last-visit": {
                "required_params": ["user_id - INTEGER", "last_visit - STRING"],
                "result": "The updated user id"
            }
        },
        "DELETE": {
            "/users": {
                "required_params": ["user_id - INTEGER"],
                "result": "The deleted user id"
            },
            "/downloads": {
                "required_params": ["download_id - INTEGER"],
                "result": "The deleted download id"
            }
        },
        "OPTIONS": {
            "/": {
                "required_params": [],
                "result": "The available routes"
            }
        }
    }