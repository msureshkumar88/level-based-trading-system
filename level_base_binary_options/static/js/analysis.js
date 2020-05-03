$.ajax({
    url: BASE_URL + 'account/charts-get',
    data: {
        'start_date': "",
        'end_date': "",
        'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
    },
    dataType: 'json',
    method: 'POST',
    success: function (data) {
        console.log(data)
        addGraph(data.data)

    }
});


function addGraph(data) {

    var accountBalance = getBalanceChart(data.balance.date, data.balance.value)
    var tradeCounts = getTradeCountChart(data.num_trades.date, data.num_trades.value)
    getTradeCountChart(data.num_trades.date, data.num_trades.value)
    Plotly.newPlot('account_balance', accountBalance.chart_data, accountBalance.layout);
    Plotly.newPlot('trade_counts', tradeCounts.chart_data,  tradeCounts.layout);


}

function getBalanceChart(date, value) {
    date = JSON.parse(date)
    value = JSON.parse(value)
    var data = {};
    data['chart_data'] = [
        {
            x: date,
            y: value,
            type: 'lines'
        }
    ];
    data['layout'] = {
        autosize: true,
        yaxis: {
            automargin: false,
        },
        xaxis: {
            automargin: false,
        },
    };
    return data
}

function getTradeCountChart(date, value) {
    date = JSON.parse(date)
    value = JSON.parse(value)
    var data = {};
    data['chart_data'] = [
        {
            x: date,
            y: value,
            type: 'lines'
        }
    ];
    data['layout'] = {
        autosize: true,
        yaxis: {
            automargin: false,
        },
        xaxis: {
            automargin: false,
        },
    };
    return data
}