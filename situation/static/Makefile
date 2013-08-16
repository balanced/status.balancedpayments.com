SHELL = /bin/sh
JS_COMPRESSOR = ./node_modules/uglify-js/bin/uglifyjs
CSS_COMPRESSOR = ./node_modules/less/bin/lessc --compress

JS_SOURCES = js/balanced.lib.src.js \
             js/status.src.js \
             js/subscribe.src.js

CSS_SOURCES = less/bootstrap-2.0/mixins.less \
			  less/bootstrap-2.0/variables.less \
              less/variables.less \
              less/base.less \
              less/subscribe.less

all: node_modules \
    js/status.min.js \
    css/status.min.css

js/status.min.js: $(JS_SOURCES)
	cat $^ | $(JS_COMPRESSOR) > $@

css/status.min.css: $(CSS_SOURCES)
	$(CSS_COMPRESSOR) $^ > $@

clean:
	rm -rf js/status.min.js
	rm -rf css/status.min.css

node_modules: package.json
	npm install
	touch node_modules