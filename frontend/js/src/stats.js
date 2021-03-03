/*!
 * Copyright (c) 2016 Jessica Tallon & Matt Molyneaux
 * Licensed under AGPLv3 (https://github.com/Inboxen/Inboxen/blob/main/LICENSE)
 */

(function($, Chart) {
    'use strict';

    var statsUrl, $userCanvas, $inboxCanvas, $emailCanvas;
    var colour1, colour2, colour3;
    var point1, point2, point3;
    var chartOpts;

    var templateOptions = "<canvas aria-label='graph' role='img'></canvas>";

    colour1 = "rgb(217, 83, 79)";
    colour2 = "rgb(51, 122, 183)";
    colour3 = "rgb(70, 198, 122)";
    point1 = "circle";
    point2 = "triangle";
    point3 = "rect";

    statsUrl = $("#stats-chart").data("url");
    $userCanvas = $(templateOptions);
    $inboxCanvas = $(templateOptions);
    $emailCanvas = $(templateOptions);

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
                fill: false,
                borderWidth: 5,
                tension: 0
            },
            point: {
                borderWidth: 5,
                radius: 5
            }
        },
        legend: {
            labels: {
                usePointStyle: true,
                fontSize: 14,
                fontColor: "rgb(51, 51, 51)"
            },
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

    Chart.Legend.prototype.afterFit = function() {
        this.height = this.height + 14;
    };

    $.get(statsUrl, function(data) {
        var userChart, inboxChart, emailChart, fakeLabels;

        if (data.dates === undefined) {
            console.error("No data returned from server");
            return;
        }

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
                        label: "With inboxes",
                        backgroundColor: colour3,
                        borderColor: colour3,
                        data: data.users.with_inboxes,
                        pointStyle: point3,
                    },
                    {
                        label: "Active",
                        backgroundColor: colour2,
                        borderColor: colour2,
                        data: data.users.active,
                        pointStyle: point2,
                    },
                    {
                        label: "Total",
                        backgroundColor: colour1,
                        borderColor: colour1,
                        data: data.users.total,
                        pointStyle: point1,
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
                        label: "Disowned",
                        backgroundColor: colour3,
                        borderColor: colour3,
                        data: data.inboxes.disowned,
                        pointStyle: point3,
                    },
                    {
                        label: "With emails",
                        backgroundColor: colour2,
                        borderColor: colour2,
                        data: data.inboxes.active,
                        pointStyle: point2,
                    },
                    {
                        label: "Total",
                        backgroundColor: colour1,
                        borderColor: colour1,
                        data: data.inboxes.total,
                        pointStyle: point1,
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
                        label: "Read",
                        backgroundColor: colour2,
                        borderColor: colour2,
                        data: data.emails.read,
                        pointStyle: point2,
                    },
                    {
                        label: "Total",
                        backgroundColor: colour1,
                        borderColor: colour1,
                        data: data.emails.total,
                        pointStyle: point1,
                    }
                ]
            },
            options: chartOpts
        });
    });
})(jQuery, Chart);
