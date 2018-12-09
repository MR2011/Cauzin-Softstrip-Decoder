from abc import ABC, abstractmethod

class AbstractHeaderExtractor(ABC):

	@abstractmethod
	def remove_horizontal_header(self):
		"""
			This method is supposed to remove the horizontal synchronization section 
			in a Cauzin Softstrip.
		"""
		pass

	@abstractmethod
	def get_bits_per_row(self):
		"""
			This method is supposed to parse the horizontal synchronization section
			and return the number of bits in each row.
		"""
		pass