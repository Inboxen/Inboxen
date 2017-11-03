/*!
 * Copyright (c) 2016 Jessica Tallon & Matt Molyneaux
 * Licensed under AGPLv3 (https://github.com/Inboxen/Inboxen/blob/master/LICENSE)
 */

(function($, Chart) {
    'use strict';

    var statsUrl, $userCanvas, $inboxCanvas, $emailCanvas;
    var colour1, colour2, fill1, fill2;
    var chartOpts;

    colour1 = "rgb(217, 83, 79)";
    colour2 = "rgb(51, 122, 183)";
    fill1 = "rgba(217, 83, 79, 0.75)";
    fill2 = "rgba(51, 122, 183, 0.75)";

    statsUrl = $("#stats-chart").data("url");
    $userCanvas = $("<canvas></canvas>");
    $inboxCanvas = $("<canvas></canvas>");
    $emailCanvas = $("<canvas></canvas>");

    chartOpts = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true
                }
            }],
            xAxes: [{
                gridLines: false
            }]
        },
        elements: {
            line: {
                tension: 0
            }
        },
        legend: {
            reverse: true
        },
        animation: {
            duration: 0, // general animation time
        },
        hover: {
            animationDuration: 0, // duration of animations when hovering an item
        },
        responsiveAnimationDuration: 0, // animation duration after a resize
    };

    $.get(statsUrl, function(data) {
        var userChart, inboxChart, emailChart, fakeLabels;

        // horrible hack to avoid printing the full dates under the X axis
        fakeLabels = new Array(data.dates.length);
        for (var i = 0; i < data.dates.length; i++) {
            fakeLabels[i] = "";
        }

        $("#users-chart").prepend($userCanvas);
        userChart = new Chart($userCanvas, {
            type: 'line',
            data: {
                labels: fakeLabels,
                datasets: [
                    {
                        label: "Users with inboxes",
                        backgroundColor: fill2,
                        borderColor: colour2,
                        data: data.active_users,
                    },
                    {
                        label: "Users",
                        backgroundColor: fill1,
                        borderColor: colour1,
                        data: data.users,
                    }
                ]
            },
            options: chartOpts
        });

        $("#inboxes-chart").prepend($inboxCanvas);
        inboxChart = new Chart($inboxCanvas, {
            type: 'line',
            data: {
                labels: fakeLabels,
                datasets: [
                    {
                        label: "Inboxes with emails",
                        backgroundColor: fill2,
                        borderColor: colour2,
                        data: data.active_inboxes,
                    },
                    {
                        label: "Inboxes",
                        backgroundColor: fill1,
                        borderColor: colour1,
                        data: data.inboxes,
                    }
                ]
            },
            options: chartOpts
        });

        $("#emails-chart").prepend($emailCanvas);
        emailChart = new Chart($emailCanvas, {
            type: 'line',
            data: {
                labels: fakeLabels,
                datasets: [
                    {
                        label: "Emails read",
                        backgroundColor: fill2,
                        borderColor: colour2,
                        data: data.read_emails,
                    },
                    {
                        label: "Emails",
                        backgroundColor: fill1,
                        borderColor: colour1,
                        data: data.emails,
                    }
                ]
            },
            options: chartOpts
        });
    });
})(jQuery, Chart);
