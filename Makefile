.PHONY: run test clean

run:
	./main.sh

test:
	./test.sh

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf public
