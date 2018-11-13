targs = --cov-report term-missing --cov results

check: clean fmt test lint

test:
	pytest $(targs)

lint:
	flake8 .

fmt:
	isort -rc .
	black .

gitclean:
	git clean -fXd

clean:
	find . -name \*.pyc -delete
	rm -rf .cache
