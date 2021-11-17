module.exports = function(grunt) {
    var sass = require('sass');

    var preprocessors = {};
    if (!process.env.SKIP_COVERAGE) {
        preprocessors["<%= dirs.js %>/src/*.js"] = ["coverage"];
    }

    grunt.initConfig({
        pkg: grunt.file.readJSON("package.json"),
        dirs: {
            build: "frontend/build",
            css: "frontend/css",
            js: "frontend/js",
            static: "inboxen/static/compiled",
            thirdparty: "node_modules",
        },
        clean: {
            build: ["<%= dirs.build %>", "<%= dirs.static %>"],
        },
        copy: {
            fonts: {
                expand: true,
                nonull: true,
                flatten: true,
                src: "<%= dirs.thirdparty %>/font-awesome/fonts/*",
                dest: "<%= dirs.static %>/fonts/",
            }
        },
        concat: {
            options: {
                sourceMap: true,
            },
            website: {
                src: [
                    "<%= dirs.thirdparty %>/jquery/dist/jquery.js",
                    "<%= dirs.js %>/src/utils.js",
                    "<%= dirs.js %>/src/copy.js",
                    "<%= dirs.js %>/src/alert.js",
                    "<%= dirs.js %>/src/home.js",
                    "<%= dirs.js %>/src/search.js",
                    "<%= dirs.js %>/src/inbox.js",
                ],
                dest: "<%= dirs.build %>/src/website.js",
                nonnull: true
            },
            stats: {
                src: [
                    "<%= dirs.thirdparty %>/patternomaly/dist/patternomaly.js",
                    "<%= dirs.thirdparty %>/chart.js/dist/Chart.js",
                    "<%= dirs.js %>/src/stats.js",
                ],
                dest: "<%= dirs.build %>/src/stats.js",
                nonnull: true
            }
        },
        uglify: {
            options: {
                mangle: true,
                compress: true,
                sourceMap: {
                    includeSources: true
                },
                output: {
                    comments: /^!/
                }
            },
            website: {
                src: ["<%= dirs.build %>/src/website.js"],
                dest: "<%= dirs.static %>/website.min.js"
            },
            stats: {
                src: ["<%= dirs.build %>/src/stats.js"],
                dest: "<%= dirs.static %>/stats.min.js"
            }
        },
        sass: {
            options: {
                implementation: sass,
                outputStyle: "compressed",
                includePaths: ["<%= dirs.thirdparty %>"],
                sourceMap: true,
                sourceMapContents: true,
                sourceMapEmbed: false
            },
            publicCss: {
                src: ["<%= dirs.css %>/inboxen.scss"],
                dest: "<%= dirs.static %>/website.css"
            }
        },
        karma: {
            options: {
                client: {
                    jasmine: {
                        random: true,
                        stopSpecOnExpectationFailure: false
                    }
                },
                configFile: "karma.conf.js",
                preprocessors: preprocessors,
                files: [
                    {
                        pattern: "<%= dirs.js %>/data/*.html",
                        type: "dom"
                    },
                    {
                        pattern: "<%= dirs.js %>/data/*.json",
                        included: false,
                        served: true,
                    },
                    "<%= dirs.thirdparty %>/jquery/dist/jquery.js",
                    "<%= dirs.thirdparty %>/chart.js/dist/Chart.js",
                    "<%= dirs.js %>/src/*.js",
                    "<%= dirs.js %>/tests/*.js"
                ]
            },
            chrome: {
                singleRun: true,
                browsers: ["ChromiumMaybeHeadless"]
            },
            firefox: {
                singleRun: true,
                browsers: ["Firefox"]
            },
            chromeDebug: {
                singleRun: false,
                browsers: ["ChromiumMaybeHeadless"]
            },
            firefoxDebug: {
                singleRun: false,
                browsers: ["Firefox"]
            },
            debug: {
                singleRun: false,
                browsers: []
            }
        },
        jshint: {
            options: {jshintrc: true},
            all: ["<%= dirs.js %>"]
        }
    });

    grunt.loadNpmTasks('grunt-contrib-clean');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks("grunt-contrib-concat");
    grunt.loadNpmTasks("grunt-contrib-uglify");
    grunt.loadNpmTasks('grunt-sass');
    grunt.loadNpmTasks('grunt-karma');
    grunt.loadNpmTasks('grunt-contrib-jshint');

    grunt.registerTask("default", ["clean", "copy", "concat", "uglify", "sass"]);
    grunt.registerTask("tests", ["karma:firefox", "karma:chrome"]);
};
