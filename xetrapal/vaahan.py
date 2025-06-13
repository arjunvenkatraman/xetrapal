#coding: utf-8
#from .aadhaar import 
import jeeva
import colored


class Vaahan(jeeva.Jeeva):
	"""
	Vaahan (meaning "vehicle" or "carrier") is a class that extends Jeeva.
	It represents an entity that can possess and manage 'astras' (tools/APIs).
	Like Jeeva, it has a profile and logging capabilities.

	Key responsibilities:
	- Managing a collection of astras.
	- Updating its profile with information about its astras.
	"""
	def __init__(self,*args, **kwargs):
		"""
		Initializes the Vaahan instance.

		Args:
			*args: Variable length argument list passed to the parent Jeeva class.
			**kwargs: Arbitrary keyword arguments passed to the parent Jeeva class.
		"""
		super(Vaahan,self).__init__(*args, **kwargs)
		self.astras={} # Dictionary to hold astra_name: astra_handle
				
	def update_astras(self):
		"""
		Updates the 'astras' list in the Vaahan's profile.
		This method serializes the types of currently loaded astras and saves them
		to the Vaahan's profile.
		"""
		self.logger.info("Trying to update astras")
		astras_info={} # Renamed to avoid conflict with self.astras
		if not self.astras: # More Pythonic check for empty dict
			self.logger.warning("I dont seem to have any astras")
		else:
			for astraname, astra_obj in self.astras.items():
				astras_info[astraname]=str(type(astra_obj))
	
		self.set_property("astras",astras_info)
		self.save_profile()
	

	def add_astra(self,astraname,astrahandle):
		"""
		Adds an 'astra' (tool/API) to the Vaahan.

		Args:
			astraname (str): The name to assign to this astra.
			astrahandle: The astra object/handle to add.
		"""
		self.astras[astraname]=astrahandle
		self.update_astras()
		
	def drop_astra(self,astraname):
		"""
		Removes and returns an 'astra' from the Vaahan.

		Args:
			astraname (str): The name of the astra to drop.

		Returns:
			The astra object/handle that was removed. Returns None if the astra
			is not found (though `pop` will raise KeyError if not found and no default given).
		"""
		self.logger.info("Dropping astra " + colored.stylize(astraname,colored.fg("violet")))
		try:
			astrahandle=self.astras.pop(astraname)
			self.update_astras()
			return astrahandle
		except KeyError:
			self.logger.error(f"Astra '{astraname}' not found, cannot drop.")
			return None

