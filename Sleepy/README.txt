Greetings, grader!

This application should be fully compatible with Windows, Linux, and OSX. Grade it where you see fit.

Also, it shouldn't blow up when used over SSH. Sorry about that.

My application uses three synchronization primitives: A condition variable in each barber thread, a 
signal in each barber thread, and a signal in each customer thread. 

The condition variable is, in this instance, what performs the locking -- as python can lock on a 
condition variable. This ensures that only one barber thread can have access to the volatile elements
of Barber (namely the list of customers) at any one point in time. It locks immediatley before customer 
logic happens, and will wait to be woken up by a customer thread, which will notify exactly 1 barber 
thread -- that is, any one barber thread that happens to be waiting on our condition variable. This
barber will acquire the lock and attend to the customer.

The event signal in barber is actually really simple -- it won't wake the thread, but it can be set
universally for the class even whilst it's sleeping. As a result, once we set it, we notify all 
barbers to wake up -- who will then see that this signal has been set, abort all customer operational
logic, and go home for the day.

The event signal in Customer is a tad more complicated -- every customer has a unique 'serviced' 
event signal. The customer waits on this signal while they're in the queue to be serviced, or while
they're being serviced. After the barber trims the hair of a customer, they will set() that 
exact customer's signal -- which will wake them back into a running state, so they will know 
they've gotten a haircut and can go home.

Effectively, the barbers are sleeping whenever they're not attending to a customer, and the 
customers are sleeping whenever they're being trimmed.

This is, indeed, a sleepy barbershop.
