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
//TODO: fix account balance does not update for winning trades
function addGraph(data) {
    if (data.hasOwnProperty('balance') && $("#account_balance").length) {
        var accountBalance = getBalanceChart(data.balance.date, data.balance.value)
        Plotly.newPlot('account_balance', accountBalance.chart_data, accountBalance.layout);
    }
    if (data.hasOwnProperty('num_trades') && $("#trade_counts").length) {
        var tradeCounts = getTradeCountChart(data.num_trades.date, data.num_trades.value)
        Plotly.newPlot('trade_counts', tradeCounts.chart_data, tradeCounts.layout);
    }

    if (data.hasOwnProperty('buy') && data.hasOwnProperty('sell') && $("#buy_sell_cht").length) {
        add_buy_sell_graph(data)
    }


}

function getBalanceChart(date, value) {
    date = JSON.parse(date);
    value = JSON.parse(value);
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
    date = JSON.parse(date);
    value = JSON.parse(value);
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

var balance_start_date = $('input[name="balance_start_date"]');
balance_start_date.change(function (val) {
    var start_date = $(this).val();
    var type = $(this).data('stayetype');
    var end_date = balance_end_date.val();
    getAnalysisDataByDate(start_date, end_date, type);
});

var balance_end_date = $('input[name="balance_end_date"]');

balance_end_date.change(function (val) {
    var start_date = balance_start_date.val()
    var type = $(this).data('stayetype');
    var end_date = $(this).val();
    getAnalysisDataByDate(start_date, end_date, type);
});

var num_trades_start_date = $('input[name="num_trades_start_date"]');
var num_trades_end_date = $('input[name="num_trades_end_date"]');

num_trades_start_date.change(function () {
    var start_date = $(this).val();
    var type = $(this).data('stayetype');
    var end_date = num_trades_end_date.val();
    getAnalysisDataByDate(start_date, end_date, type);
});

num_trades_end_date.change(function () {
    var start_date = num_trades_start_date.val();
    var type = $(this).data('stayetype');
    var end_date = $(this).val();
    getAnalysisDataByDate(start_date, end_date, type);
});

var buy_sell_start_date = $('input[name="buy_sell_start_date"]');
var buy_sell_end_date = $('input[name="buy_sell_end_date"]');

buy_sell_start_date.change(function () {
    var start_date = $(this).val();
    var type = $(this).data('stayetype');
    var end_date = buy_sell_end_date.val()
    getAnalysisDataByDate(start_date, end_date, type)
});
buy_sell_end_date.change(function () {
    var start_date = buy_sell_start_date.val();
    var type = $(this).data('stayetype');
    var end_date = $(this).val();
    getAnalysisDataByDate(start_date, end_date, type)
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
            console.log(data)
            if (Object.keys(data).length !== 0) {
            }
            if (type === "buy_sell") {
                add_buy_sell_graph(data.data)
            }
            addGraph(data)


        }
    });

}

function add_buy_sell_graph(data) {
    var buy = JSON.parse(data.buy.value);
    var sell = JSON.parse(data.sell.value);
    var date = JSON.parse(data.buy.date);
    console.log(buy)
    console.log(sell)
    console.log(date)
    // console.log(data)
    var trace1 = {
        x: date,
        y: buy,
        name: 'Buy',
        type: 'bar'
    };

    var trace2 = {
        x: date,
        y: sell,
        name: 'Sell',
        type: 'bar'
    };

    var data = [trace1, trace2];

    var layout = {
        barmode: 'group',
        xaxis: {
      tickformat: '%Y-%m-%d'
    }
    };

    Plotly.newPlot('buy_sell_cht', data, layout);
}