# use ab to -n number hit -c concurrent -s timeout

test-hello:
	ab -n 20 -c 1 -s 120 http://localhost:8000/hello

test-random:
	ab -n 20 -c 1 -s 120 http://localhost:8000/random
