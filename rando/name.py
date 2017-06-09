import itertools
from rando.word import Word

class Name(object):
	def __init__(self, name):
		self.name = unicode(name)
		self.words = {}
		for word in self.name.split(" "):
			self.words[word] = []
		self.chunks = []

	def __str__(self):
		return self.name

	def __repr__(self):
		return unicode({"name": self.name, "words": self.words})

	def __eq__(self, name):
		return self.name == name.name

	def count_unaccounted(self):
		cnt = 0
		for word in self.words.keys():
			for meaning in self.words[word]:
				cnt += meaning.count_unaccounted()
		return cnt

	def find_chunks(self):
		l = self.name.lower()
		candidates = []
		for words in self.word_db.values():
			if words[0].word_has_meaning(l):
				self.chunks.extend(words)

	def find_meaning(self, word_db):
		self.word_db = word_db
		self.find_chunks()
		for word in self.words.keys():
			w = Word(word)
			meanings = w.extract_meanings(self.chunks)
			retmeanings = []
			for meaning in meanings:
				if meaning not in retmeanings:
					self.words[word].append(meaning)
			if len(self.words[word]) == 0:
				self.words[word].append(w)
		self.reduce()

	def reduce(self):
		self.filter_for_unaccounted()
		self.filter_for_complexity()

	def filter_for_unaccounted(self):
		for word in self.words.keys():
			meanings = self.words[word]
			max_unaccounted = 100
			for meaning in meanings:
				if meaning.count_unaccounted() < max_unaccounted:
					max_unaccounted = meaning.count_unaccounted()
			new_meanings = []
			for meaning in meanings:
				if meaning.count_unaccounted() == max_unaccounted:
					if meaning not in new_meanings:
						if meaning != '':
							new_meanings.append(meaning)
			self.words[word] = new_meanings

	def filter_for_complexity(self):
		for word in self.words.keys():
			meanings = self.words[word]
			max_complexity = 100
			for meaning in meanings:
				if meaning.size() < max_complexity:
					max_complexity = meaning.size()
			new_meanings = []
			for meaning in meanings:
				if meaning.size() == max_complexity:
					if meaning not in new_meanings:
						if len(meaning.word) > 0:
							new_meanings.append(meaning)
			self.words[word] = new_meanings

	def has_name(self):
		for word in self.words.keys():
			for meaning in self.words[word]:
				if meaning.has_name():
					return True
		return False

	def has_saint(self):
		for word in self.words.keys():
			for meaning in self.words[word]:
				if meaning.has_saint():
					return True
		return False

	def get_samples(self):
		usage_set = set()
		for word_list in self.words.values():
			for word in word_list:
				usage_set = usage_set.union(word.get_samples())
		return usage_set

	def get_lone_samples(self):
		usage_set = set()
		for word_list in self.words.values():
			for word in word_list:
				usage_set = usage_set.union(word.get_lone_samples())
		return usage_set

	def get_structure(self):
		structure = []
		for word in self.name.split(" "):
			group = set([w.get_structure() for w in self.words[word]])
			structure.append(group)
		return set(itertools.product(*structure))

def load_names(data):
	names = []
	for country in data.keys():
		for region in data[country].keys():
			names.extend(data[country][region])
	names.sort()
	newnames = []
	for name in names:
		if len(newnames) == 0:
			newnames.append(unicode(name))
		elif newnames[-1] != name:
			newnames.append(unicode(name))
	return [Name(name) for name in newnames]

