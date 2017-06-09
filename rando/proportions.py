import random

class Generator(object):
	def __init__(self, tag_db, elements):
		self.tag_db = tag_db
		self.elements = elements

	def add_item(self, key, proportion):
		self.elements[key] = proportion

	def select(self, *tags):
		items = self.elements.items()
		if len(tags) > 0:
			items = self.filter_for_tag(*tags).items()
		if len(items) == 0:
			return None
		return weighted_choice(items)

	def has_tag(self, *tags):
		usages = self.filter_for_tags(*tags)
		if len(usages) > 0:
			return True
		return False

	def filter_for_tag(self, *tags):
		keys = []
		for tag in tags:
			keys.extend(self.tag_db[tag])
		keys = set(keys)
		usages = {}
		for key in keys:
			if self.elements.has_key(key):
				usages[key] = self.elements[key]
		return usages

class MeaningGenerator(object):
	def __init__(self, meaning_db, tag_db, proportions):
		self.meaning_db = meaning_db
		self.tag_db = tag_db
		self.generators = {}
		self.load_parts(proportions)

	def load_parts(self, proportions, *addkeys):
		for usage, proportion in proportions.items():
			meanings = self.meaning_db[usage]
			keys = set([m.key() for m in meanings])
			for key in keys:
				if addkeys:
					key = list(key)
					key.extend(addkeys)
					key = tuple(key)
				generator = self.generators.setdefault(key, Generator(self.tag_db, {}))
				generator.add_item(usage, proportion)

	def select(self, key, *tags):
		return self.generators[key].select(*tags)

class NameGenerator(object):
	def __init__(self, meaning_db, meaning_gen, structs):
		self.meaning_db = meaning_db
		self.meaning_gen = meaning_gen
		self.structs = structs

	def select(self, *tags):
		items = self.structs.items()
		struct = weighted_choice(items)
		if len(tags) == 0:
			return self.__select_no_tag__(struct)
		else:
			return self.__select_tags__(struct, *tags)

	def __select_no_tag__(self, struct):
		words = []
		for w in struct:
			keys = []
			for key in w:
				keys.append(self.meaning_gen.select(key))
			words.append(keys)
		newname = NewName(struct, self.meaning_db, words)
		return newname

	def __select_tags__(self, struct, *tags):
		name_pool = []
		name_pool.append(self.__select_no_tag__(struct))
		for tag in tags:
			name_pool.append(self.__select_tag__(struct, tag))
		words = []
		for i in range(0, len(struct)):
			keys = []
			for j in range(0, len(struct[i])):
				pool = []
				for elem in name_pool:
					e = elem.name[i][j]
					if e:
						pool.append(e)
				keys.append(random.choice(pool))
			words.append(keys)
		return NewName(struct, self.meaning_db, words)

	def __select_tag__(self, struct, tag):
		words = []
		for w in struct:
			keys = []
			for key in w:
				keys.append(self.meaning_gen.select(key, tag))
			words.append(keys)
		newname = NewName(struct, self.meaning_db, words)
		return newname

class NewName(object):
	def __init__(self, struct, meaning_db, name):
		self.struct = struct
		self.meaning_db = meaning_db
		self.name = name

	def __str__(self):
		words = []
		for w in self.name:
			for e in w:
				words.append(e.replace("-", ""))
			words.append(" ")
		return "".join(words).strip()

	def __repr__(self):
		words = []
		for w in self.name:
			for e in w:
				words.append(self.meaning_db[e])
		return repr(words)

	def description(self):
		results = []
		for word in self.name:
			single = False
			if len(word) == 1:
				single = True
			for e in word:
				part = []
				if single:
					part.append(e.replace("-", ""))
				else:
					part.append(e)
				part.append(" (")
				meaning = self.meaning_db[e]
				meanings = []
				for m in meaning:
					meanings.append(self.__find_meaning__(m))
				part.append(" or ".join(meanings))
				part.append(")")
				results.append("".join(part))
		return " ".join(results)

	def __find_meaning__(self, meaning):
		roots = self.__find_roots__(meaning)
		meanings = meaning.meanings
		return "%s %s" % (roots, ", ".join(meanings))

	def __find_roots__(self, meaning):
		roots = []
		if meaning.sources.has_key("old_english"):
			roots.append("EN")
		if meaning.sources.has_key("old_scandinavian"):
			roots.append("SC")
		if meaning.sources.has_key("old_french"):
			roots.append("FR")
		if meaning.sources.has_key("celtic_mix"):
			roots.append("CL")
		if meaning.sources.has_key("latin"):
			roots.append("LA")
		if meaning.sources.has_key("germanic"):
			roots.append("GE")
		if meaning.sources.has_key("greek"):
			roots.append("GR")
		return "/".join(roots)

def word_to_key(word):
	elements = []
	for element in word:
		key = [element["location"]]
		if element.get("name", False):
			key.append("name")
		if element.get("saint", False):
			key.append("saint")
		elements.append(key)
	if len(word) == 1:
		elements[0].append("single")
	return tuple([tuple(e) for e in elements])

def load_proportions(data, meaning_db, tag_db):
	usages = data["usages"]
	mg = MeaningGenerator(meaning_db, tag_db, usages)
	single_usages = data["single_usages"]
	mg.load_parts(single_usages, "single")
	structures = data["structures"]
	struct = {}
	for element in structures:
		proportion = element["proportion"]
		words = tuple([word_to_key(w) for w in element["words"]])
		struct[words] = proportion
	return NameGenerator(meaning_db, mg, struct)

def weighted_choice(choices):
	"""Like random.choice, but each element can have a different chance of
	being selected.

	choices can be any iterable containing iterables with two items each.
	Technically, they can have more than two items, the rest will just be
	ignored.  The first item is the thing being chosen, the second item is
	its weight.  The weights can be any numeric values, what matters is the
	relative differences between them.
	"""
	space = {}
	current = 0
	for choice, weight in choices:
		if weight > 0:
			space[current] = choice
			current += weight
	rand = random.uniform(0, current)
	for key in sorted(space.keys() + [current]):
		if rand < key:
			return choice
		choice = space[key]
	return None
