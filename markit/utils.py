class objFromDict(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
               setattr(self, a, [objFromDict(x) if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, objFromDict(b) if isinstance(b, dict) else b)
			

ERR = dict(	
	REGISTER = dict(
		REQUIRED = dict(
			USERNAME = "username is required",
			PW = 'password is required',
			EMAIL = 'email is required'
		),
		ENROLLED = 'already registered'
	),
	LOGIN = dict(
		INCORRECT = dict(
			EMAIL = "incorrect email",
			PW = 'incorrect passward'
		)
	),
	VERIFY = dict(
		COMPLETE = "verified",
		UNCOMPLETE = "wrong page"
	),
	CONFIGURE = dict(
		SUCCESS = "CONFIGURATION SUCCESS",
		FAIL = dict(
			PW = "PW WRONG",
			GENERAL = "CONFIGURATION FAIL"
		)
	)
)
ERR = objFromDict(ERR)