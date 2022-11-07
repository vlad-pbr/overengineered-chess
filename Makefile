build:
	if [ "${NAME}" = "client" ]; then \
		docker build -t ${NAME} ${NAME}; \
	else \
		cd ${NAME} && tar -czh . | docker build - -t ${NAME}; \
	fi;

run:
	docker run --name $(shell echo ${NAME} | cut -d: -f 1) -d --network host ${NAME}

test:
	pip install pytest==7.2.0 requests==2.28.1

	docker rm -f redis || true
	$(MAKE) run NAME=redis:7.0.5

	cd ${NAME} && pytest

	docker rm -f redis

clean:
	docker rm -f client gateway move_validator endgame_validator redis || true

all: clean

	$(MAKE) run NAME=redis:7.0.5

	for IMAGE in endgame_validator move_validator gateway; do \
		$(MAKE) test NAME=$$IMAGE; \
		$(MAKE) build NAME=$$IMAGE; \
		$(MAKE) run NAME=$$IMAGE; \
	done

	#$(MAKE) build NAME=client
	#$(MAKE) run NAME=client