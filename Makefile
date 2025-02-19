# use ab to -n number hit -c concurrent -s timeout

test-hello:
	ab -n 20 -c 1 -s 120 http://localhost:8000/hello

test-random:
	ab -n 20 -c 1 -s 120 http://localhost:8000/random

up:
	docker-compose up --build -d 

down:
	docker-compose down

simulate:
	locust -f simulate.py --headless --users 10 --spawn-rate 1 -H http://localhost:18123
