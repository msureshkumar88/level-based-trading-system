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

//TODO: add more charts and filters
function addGraph(data) {
    if (data.hasOwnProperty('balance')) {
        var accountBalance = getBalanceChart(data.balance.date, data.balance.value)
        Plotly.newPlot('account_balance', accountBalance.chart_data, accountBalance.layout);
    }
    if (data.hasOwnProperty('num_trades')) {
        var tradeCounts = getTradeCountChart(data.num_trades.date, data.num_trades.value)
        Plotly.newPlot('trade_counts', tradeCounts.chart_data, tradeCounts.layout);
    }


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
        autosize: false,
        width: 930,
        height: 450,
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
        autosize: false,
        width: 930,
        height: 450,
        yaxis: {
            automargin: false,
        },
        xaxis: {
            automargin: false,
        },
    };
    return data
}

var balance_start_date = $('input[name="balance_start_date"]')
balance_start_date.change(function (val) {
    var start_date = $(this).val();
    var type = $(this).data('stayetype');
    var end_date = balance_end_date.val();
    getAnalysisDataByDate(start_date, end_date, type);
});

var balance_end_date = $('input[name="balance_end_date"]')

balance_end_date.change(function (val) {
    var start_date = balance_start_date.val()
    var type = $(this).data('stayetype');
    var end_date = $(this).val();
    getAnalysisDataByDate(start_date, end_date, type);
});

function getAnalysisDataByDate(start_date, end_date, type) {
    $.ajax({
        url: BASE_URL + 'account/charts-get',
        data: {
            'start_date': start_date,
            'end_date': end_date,
            'type': type,
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        dataType: 'json',
        method: 'POST',
        success: function (data) {
            data = data.data
            console.log(data)
            if (Object.keys(data).length !== 0) {
            }
            addGraph(data)


        }
    });

}