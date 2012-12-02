#!/usr/bin/env node


// This script joins js files together and outputs to stdout.
// .js files are passed straight in with a little "compiled from" leader.
// assignment, like this: R.dom['jadefilename'] = 'compiledhtml';

var fs = require('fs')
    , async = require('async');

var argParts = process.argv.slice(2).map(function(file) {
    return jsPart(file);
});

var VERSION = '0';

async.series([prepare].concat(headerPart).concat(argParts).concat(footerPart));

function prepare(done) {
    VERSION = fs.readFileSync('version').toString().trim();
    done();
}

function headerPart(done) {

    var header = fs.readFileSync('src/header.js') + '';
    header = header.replace(/\{VERSION\}/,VERSION);

    process.stdout.write(
        header
            + '\n(function(ctx) {'
            + '\n    "use strict";'
    );

    done();
};

function footerPart(done) {
    process.stdout.write(
        '\n    window.Balanced = Balanced;' +
            '\n' +
            '\n})(this);' +
            '\n'
    );
    done();
};

function jsPart(jsfile) {
    return function(done) {
        fs.readFile(jsfile, function(err, data){
            data = ('' + data).replace(/\{VERSION\}/,VERSION);

            process.stdout.write(leader(jsfile) + data);

            done();
        });
    };
}


function leader(file) {
    var jsstr = '';
    jsstr += "\n\n//////////////////////////////////////////////////\n";
    jsstr += "// Compiled from " + file + "\n";
    jsstr += "//////////////////////////////////////////////////\n\n";

    return jsstr;
}
