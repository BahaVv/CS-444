import threading
import time
import random

CUSTOMERS = 256
BARBERS = 4

ARRIVAL_WAIT = 0.05

def wait():
	time.sleep(ARRIVAL_WAIT * random.random())

class Barber(threading.Thread):
	condition = threading.Condition() # Acquired whenever customers is being accesed
	customers = []
	should_stop = threading.Event() # Since this is declared and instantiated in the class, rather than declared in the class
									# and instantiated in a function (like serviced in Customer), all barbers have the same
									# event.

	def run(self):
		while True:
			with self.condition: # Condition locked automagically
				if not self.customers:
					# No customers, snore...
					print "{} is falling asleep...".format(self)
					self.condition.wait() # Wait w/ no timeout until notified. Releases lock until awakened.
				# Get the next customer
				if self.should_stop.is_set():
					# Main has told us barbers should stop
					return # Thread is destroyed as main returns
				if not self.customers:
					print "{} woke up to help a customer, but was just day-dreaming".format(self) # NO IDEA WHAT CAUSES THIS
					continue
				customer = self.customers.pop()
				print "{} is waking up to trim {}!".format(self, customer)
			# Actually service the next customer
			customer.trim()

class Customer(threading.Thread):
	WAIT = 0.05
	serviced = None # We can rely upon this being an Event by the time we need to call it

	def wait(self):
		time.sleep(self.WAIT * random.random())

	def trim(self):  
		# Note: Called from Barber thread
		# Get a haircut
		print "{} is getting a trim!".format(self)
		self.wait()
		#Notify customer cut is done. Resume run()/finish execution
		self.serviced.set()

	def run(self):
		self.serviced = threading.Event()
		# Grab the barbers' attention, add ourselves to the customers,
		with Barber.condition: # Make sure to acquire lock from condition, so we know nothing else is altering sensitive items
							   # in Barber class
			Barber.customers.append(self)
			Barber.condition.notify(1) # If we woke more than one thread, the program would die horrifically :D

		# and wait to be serviced
		print "{} has fallen asleep while waiting to be serviced!"
		self.serviced.wait() # When this is set in trim, we'll return
		print "{} is leaving!".format(self)

def main():
	print "Welcome to the sleepy barbershop! Where none of our barbers will fall asleep on a customer!\n"

	for b in range(BARBERS):
		Barber().start()

	all_customers = []

	for c in range(CUSTOMERS):
		wait()
		print"A new customer has arrived!"
		c = Customer()
		all_customers.append(c)
		c.start()
		print "Give a warm welcome to {}!".format(c)

	for c in all_customers:
		c.join()  # Wait for all customers to leave. Thread join.

	print "\nAll customers have left! Clean up, barbers!\n"

	# Grab the barbers' attention and tell them all that it's time to leave
	Barber.should_stop.set() # Set should_stop. run function will check for this and return
							 # This is fine because the set across all instances of Barber will be atomic in Python
	with Barber.condition: # Make sure we can acquire lock from the condition before notifying threads waiting on it
		Barber.condition.notify_all() # Wake all threads! Allow them to see the flag and return

	print "All barbers have gone home for the day. Goodnight!\n"


if __name__ == '__main__':
	main()
