def traverse(obj: dict, search_term: str):
	# Traverse through json dict
	for k,v in obj.items():
		if isinstance(v, str) and k == search_term:
			print(f"{v} is instance of str")
			return v
		elif isinstance(v, dict):
			print(f"{v} is instance of dict")
			traverse(v, search_term)
		elif isinstance(v, list):
			print(f"{v} is instance of list")
			for eac in v:
				traverse(eac, search_term)
