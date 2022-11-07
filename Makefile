build:
	cd ${NAME} && tar -czh . | docker build - -t ${NAME}

run:
	docker run --name $(shell echo ${NAME} | cut -d: -f 1) -d --network host ${NAME}

test:
	echo TODO

clean:
	docker rm -f client gateway move_validator endgame_validator redis || true

all: clean

	$(MAKE) run NAME=redis:7.0.5

	for IMAGE in endgame_validator move_validator gateway; do \
		$(MAKE) test NAME=$$IMAGE; \
		$(MAKE) build NAME=$$IMAGE; \
		$(MAKE) run NAME=$$IMAGE; \
	done

	$(MAKE) build NAME=client
	$(MAKE) run NAME=client