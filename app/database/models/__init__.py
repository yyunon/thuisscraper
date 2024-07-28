from sqlalchemy import inspect

def attrs(cls): 
	return inspect(cls).attrs.keys()