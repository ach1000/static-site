.PHONY: run test clean build

run:
	./main.sh

test:
	./test.sh

build:
	./build.sh

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf docs
