function browserNormaliser(browser) {
    return browser.toLowerCase().split(/[ /-]/)[0];
}

module.exports = function(config) {
    var chromeOpts = {
        base: "Chromium"
    };

    if (process.env.CI) {
        chromeOpts = {
            base: "ChromiumHeadless",
            flags: ["--no-sandbox"]
        };
    }

    var reporters = ['progress', 'kjhtml'];
    if (!process.env.SKIP_COVERAGE) {
        reporters.push("coverage");
    }

    config.set({
        logLevel: config.LOG_INFO,
        frameworks: ['jasmine'],
        customLaunchers: {
            ChromiumMaybeHeadless: chromeOpts
        },
        reporters: reporters,
        coverageReporter: {
            reporters: [
                {
                    type: 'lcov',
                    dir: 'coverage/',
                    subdir: '.'
                },
                {type: "text-summary"},
                {
                    type: "html",
                    dir: "htmlcov",
                    subdir: browserNormaliser
                }
            ]
        }
    });
};
