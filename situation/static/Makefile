SHELL = /bin/sh
JS_COMPRESSOR = ./node_modules/uglify-js/bin/uglifyjs
CSS_COMPRESSOR = ./node_modules/less/bin/lessc --compress

JS_SOURCES = $(js/status.src.js)
CSS_SOURCES = $(less/base.less)

all: node_modules \
    js/status.min.js \
    css/status.min.css

js/status.min.js: js/status.src.js
	$(JS_COMPRESSOR) $^ > $@

css/status.min.css: less/base.less
	$(CSS_COMPRESSOR) $^ > $@

clean:
	rm -rf js/status.min.js
	rm -rf css/status.min.css

node_modules: package.json
	npm install
	touch node_modules
