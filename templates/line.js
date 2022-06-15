var ctx = document.getElementById("lineChart").getContext("2d")
    var lineChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: {{ times | safe }},
            datasets: [
                {
                    label: "My Rating",
                    data: {{ ratings | safe }},
                    fill: true,
                    borderColor: "rgb(75, 192, 192)",
                    lineTension: 0.1
                }
            ]
        },
        options: {
            scales: {
            xAxes: [{
                ticks: {
                    display: false //this will remove only the label
                }
            }]
        }
            }
    });