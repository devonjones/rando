
class Meaning(object):
	def __init__(self, usage, tags, meanings, sources):
		self.usage = usage
		self.tags = tags
		self.meanings = meanings
		self.sources = sources
		self.__set_location__()

	def __set_location__(self):
		if self.usage.startswith('-') and self.usage.endswith('-'):
			self.location = 'inner'
		elif self.usage.endswith('-'):
			self.location = 'pre'
		else:
			self.location = 'post'

	def __str__(self):
		return self.usage.lower().replace("-", "")

	def __repr__(self):
		return "{usage: %s, tags: %s, meanings: %s}, sources: %s, location: %s}" % (self.usage, self.tags, self.meanings, self.sources, self.location)

	def word_has_meaning(self, word):
		if word.find(unicode(self)) > -1:
			return True
		return False

	def test(self, word):
		if self.location == "pre":
			if word.lower().startswith(unicode(self)):
				return [self, word.lower().replace(unicode(self), "")]
		elif self.location == "post":
			if word.lower().endswith(unicode(self)):
				return [word.replace(unicode(self), ""), self]
		else:
			if word.find(unicode(self)) > -1:
				parts = word.split(unicode(self))
				return [parts[0], self, parts[1]]

	def is_name(self):
		for tag in self.tags:
			if tag in ("female name", "male name", "family name"):
				return True
		return False

	def is_saint(self):
		for tag in self.tags:
			if tag in ("saint"):
				return True
		return False

	def key(self):
		key = [self.location]
		if self.is_name():
			key.append("name")
		elif self.usage.replace("-", "").lower() == 'saint':
			key.append("saint")
		return tuple(key)

def load_meanings(data):
	meaning_db = {}
	tags_db = {}
	for subject in data:
		tags = subject['modifier_tags']
		meanings = subject['meaning']
		for word in subject["words"]:
			usage = word["modern_usage"]
			sources = word
			del sources["modern_usage"]
			meaning = Meaning(usage, tags, meanings, sources)
			for tag in tags:
				t = tags_db.setdefault(tag, [])
				t.append(usage)
			w = meaning_db.setdefault(usage, [])
			w.append(meaning)
			if meaning.is_name():
				if not usage.endswith('s'):
					plural = "%ss" % usage
					plural_meaning = Meaning(plural, tags, meanings, sources)
					for tag in tags:
						t = tags_db.setdefault(tag, [])
						t.append(plural)
					w = meaning_db.setdefault(plural, [])
					w.append(plural_meaning)
	return meaning_db, tags_db
