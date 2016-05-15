/*!
 * Copyright (c) 2016 Jessica Tallon & Matt Molyneaux
 * Licensed under AGPLv3 (https://github.com/Inboxen/Inboxen/blob/master/LICENSE)
 */

(function($, Chart) {
    'use strict';

    var statsUrl, $userCanvas, $inboxCanvas, $emailCanvas;
    var colour1, colour2, fill1, fill2;

    colour1 = "rgb(217, 83, 79)";
    colour2 = "rgb(51, 122, 183)";
    fill1 = "rgba(217, 83, 79, 0.75)";
    fill2 = "rgba(51, 122, 183, 0.75)";

    statsUrl = $("#stats-chart").data("url");
    $userCanvas = $("<canvas></canvas>");
    $inboxCanvas = $("<canvas></canvas>");
    $emailCanvas = $("<canvas></canvas>");

    // override some defaults
    Chart.defaults.global.responsive = true;
    Chart.defaults.global.maintainAspectRatio = false;
    Chart.defaults.global.animation = false;
    Chart.defaults.global.scaleBeginAtZero = true;
    Chart.defaults.global.showTooltips = false;
    Chart.defaults.global.bezierCurve = false;

    // hack to bypass evil "new Function"
    Chart.defaults.global.tooltipTitleTemplate = function(obj) {
        return obj.label;
    };
    Chart.defaults.global.tooltipTemplate = function(obj) {
        var out = ""
        if (obj.label) {
            out = out + obj.label + ": ";
        }
        out = out + obj.value;
        return out
    };
    Chart.defaults.global.multiTooltipTemplate = function(obj) {
        return obj.value;
    };
    Chart.defaults.global.scaleLabel = function(obj) {
        return obj.value;
    };

    $.get(statsUrl, function(data) {
        var userChart, inboxChart, emailChart, fakeLabels;
        var userLineChart, inboxLineChart, emailLineChart;

        // horrible hack to avoid printing the full dates under the X axis
        fakeLabels = new Array(data.dates.length);
        for (var i = 0; i < data.dates.length; i++) {
            fakeLabels[i] = "";
        }

        $("#users-chart").prepend($userCanvas);
        userChart = new Chart($userCanvas[0].getContext("2d"));
        userChart.Line({
            labels: fakeLabels,
            datasets: [
                {
                    label: "Users",
                    fillColor: fill1,
                    strokeColor: colour1,
                    data: data.users
                },
                {
                    label: "Users with inboxes",
                    fillColor: fill2,
                    strokeColor: colour2,
                    data: data.active_users
                }
            ]
        },
        {
            pointDot: false,
            scaleShowVerticalLines: false
        });

        $("#inboxes-chart").prepend($inboxCanvas);
        inboxChart = new Chart($inboxCanvas[0].getContext("2d"));
        inboxChart.Line({
            labels: fakeLabels,
            datasets: [
                {
                    label: "Inboxes",
                    fillColor: fill1,
                    strokeColor: colour1,
                    data: data.inboxes
                },
                {
                    label: "Inboxes with emails",
                    fillColor: fill2,
                    strokeColor: colour2,
                    data: data.active_inboxes
                }
            ]
        },{
            pointDot: false,
            scaleShowVerticalLines: false
        });

        $("#emails-chart").prepend($emailCanvas);
        emailChart = new Chart($emailCanvas[0].getContext("2d"));
        emailChart.Line({
            labels: fakeLabels,
            datasets: [
                {
                    label: "Emails",
                    fillColor: fill1,
                    strokeColor: colour1,
                    data: data.emails
                },
                {
                    label: "Emails read",
                    fillColor: fill2,
                    strokeColor: colour2,
                    data: data.read_emails
                }
            ]
        },{
            pointDot: false,
            scaleShowVerticalLines: false
        });
    });
})(jQuery, Chart);
