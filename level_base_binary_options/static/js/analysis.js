var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();

if (csrfmiddlewaretoken) {
    $.ajax({
        url: BASE_URL + 'account/charts-get',
        data: {
            'start_date': "",
            'end_date': "",
            'csrfmiddlewaretoken': csrfmiddlewaretoken
        },
        dataType: 'json',
        method: 'POST',
        success: function (data) {
            addGraph(data.data)
            fill_dashboard(data.data)

        }
    });
}


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

    if (data.hasOwnProperty('won') && data.hasOwnProperty('loss') && $("#win_loss_count_cht").length) {
        add_won_loss_count_graph(data)
    }

    if (data.hasOwnProperty('d_won') && data.hasOwnProperty('d_loss') && $("#win_loss_amount_cht").length) {
        add_won_loss_amount_graph(data)
    }

    if (data.hasOwnProperty('BINARY') && data.hasOwnProperty('LEVELS') && $("#binary_levels_cht").length) {
        add_binary_levels_graph(data)
    }

    if (data.hasOwnProperty('LEVEL_1') && data.hasOwnProperty('LEVEL_2') &&
        data.hasOwnProperty('LEVEL_3') && data.hasOwnProperty('LEVEL_4') && $("#level_selection_cht").length) {
        add_level_selection_graph(data)
    }
    if (data.hasOwnProperty('LEVEL_1_INVST') && data.hasOwnProperty('LEVEL_2_INVST') &&
        data.hasOwnProperty('LEVEL_3_INVST') && data.hasOwnProperty('LEVEL_4_INVST') && $("#level_investment_cht").length) {
        add_level_investment_graph(data)
    }
    if (data.hasOwnProperty('LEVEL_1_WON_COUNT') && data.hasOwnProperty('LEVEL_2_WON_COUNT') &&
        data.hasOwnProperty('LEVEL_3_WON_COUNT') && data.hasOwnProperty('LEVEL_4_WON_COUNT') && $("#level_won_loss_counts_cht").length) {
        add_levels_won_loss_counts_graph(data)
    }
    if ($("#level_won_loss_amount_cht").length) {
        add_levels_won_loss_amount_graph(data)
    }

    if ($("#total_won_loss_cht").length) {
        add_all_won_loss_graph(data)
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


var win_loss_count_start_date = $('input[name="win_loss_count_start_date"]');
var win_loss_count_end_date = $('input[name="win_loss_count_end_date"]');

win_loss_count_start_date.change(function () {
    var start_date = $(this).val();
    var type = $(this).data('stayetype');
    var end_date = win_loss_count_end_date.val();
    getAnalysisDataByDate(start_date, end_date, type);
});

win_loss_count_end_date.change(function () {
    var end_date = $(this).val();
    var type = $(this).data('stayetype');
    var start_date = win_loss_count_start_date.val();
    getAnalysisDataByDate(start_date, end_date, type);
});

var win_loss_amount_start_date = $('input[name="win_loss_amount_start_date"]');
var win_loss_amount_end_date = $('input[name="win_loss_amount_end_date"]');

win_loss_amount_start_date.change(function () {
    var start_date = $(this).val();
    var type = $(this).data('stayetype');
    var end_date = win_loss_amount_end_date.val()
    getAnalysisDataByDate(start_date, end_date, type);
});
win_loss_amount_end_date.change(function () {
    var end_date = $(this).val();
    var type = $(this).data('stayetype');
    var start_date = win_loss_amount_start_date.val()
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
            if (Object.keys(data).length !== 0) {
            }
            if (type === "buy_sell") {
                add_buy_sell_graph(data.data)
            }
            if (type === "win_loss_count") {
                add_won_loss_count_graph(data.data)
            }
            if (type === "win_loss_amount") {
                add_won_loss_amount_graph(data.data)
            }
            addGraph(data)


        }
    });

}

function add_buy_sell_graph(data) {
    var buy = JSON.parse(data.buy.value);
    var sell = JSON.parse(data.sell.value);
    var date = []

    var b_date = JSON.parse(data.buy.date);
    var s_date = JSON.parse(data.sell.date);

    if (b_date.length !== 0){
        date = b_date
    }
    if (s_date.length !== 0){
        date = s_date
    }
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
    var config = {responsive: true}
    var layout = {
        autosize: true,
        barmode: 'group',
        xaxis: {
            tickformat: '%Y-%m-%d'
        }
    };

    Plotly.newPlot('buy_sell_cht', data, layout, config);
}

function add_won_loss_count_graph(data) {
    var won = JSON.parse(data.won.value);
    var loss = JSON.parse(data.loss.value);
    var date = [];
    var w_date = JSON.parse(data.won.date);
    var l_date = JSON.parse(data.loss.date);

    if (w_date.length !== 0){
        date = w_date
    }
    if (l_date.length !== 0){
        date = l_date
    }
    var trace1 = {
        x: date,
        y: won,
        mode: 'lines+markers',
        name: 'Won',
        line: {color: '#28a745'}

    };

    var trace2 = {
        x: date,
        y: loss,
        mode: 'lines+markers',
        name: 'Loss',
        line: {color: '#dc3545'}
    };
    var layout = {
        autosize: true,
        xaxis: {
            tickformat: '%Y-%m-%d'
        }
    };

    var c_data = [trace1, trace2];

    Plotly.newPlot('win_loss_count_cht', c_data, layout);
}

function add_won_loss_amount_graph(data) {
    var won = JSON.parse(data.d_won.value);
    var loss = JSON.parse(data.d_loss.value);
    var date = [];

    var w_date = JSON.parse(data.d_won.date);
    var l_date = JSON.parse(data.d_loss.date);
    if (w_date.length !== 0){
        date = w_date
    }

    if (l_date.length !== 0){
        date = l_date
    }
    var trace1 = {
        x: date,
        y: won,
        mode: 'lines+markers',
        name: 'Won amount',
        line: {color: '#28a745'}
    };

    var trace2 = {
        x: date,
        y: loss,
        mode: 'lines+markers',
        name: 'Loss amount',
        line: {color: '#dc3545'}
    };
    var layout = {
        autosize: true,
        xaxis: {
            tickformat: '%Y-%m-%d'
        }
    };

    var c_data = [trace1, trace2];

    Plotly.newPlot('win_loss_amount_cht', c_data, layout);
}

function add_binary_levels_graph(data) {
    var c_data = [{
        values: [data.BINARY, data.LEVELS],
        labels: ["Binary Trades", 'Levels based Trades'],
        type: 'pie'
    }];

    var layout = {
        autosize: true,
    };

    Plotly.newPlot('binary_levels_cht', c_data, layout);
}

function add_level_selection_graph(data) {
    var c_data = [
        {
            x: ['level 1', 'level 2', 'level 3', 'level 4'],
            y: [data.LEVEL_1, data.LEVEL_2, data.LEVEL_3, data.LEVEL_4],
            type: 'bar'
        }
    ];

    Plotly.newPlot('level_selection_cht', c_data);
}

function add_level_investment_graph(data) {
    var c_data = [
        {
            x: ['level 1', 'level 2', 'level 3', 'level 4'],
            y: [data.LEVEL_1_INVST, data.LEVEL_2_INVST, data.LEVEL_3_INVST, data.LEVEL_4_INVST],
            type: 'bar'
        }
    ];

    Plotly.newPlot('level_investment_cht', c_data);
}

function add_levels_won_loss_counts_graph(data) {
    var trace1 = {
        x: ['level 1', 'level 2', 'level 3', 'level 4'],
        y: [data.LEVEL_1_WON_COUNT, data.LEVEL_2_WON_COUNT, data.LEVEL_3_WON_COUNT, data.LEVEL_4_WON_COUNT],
        type: 'bar',
        name: 'Won trades',
        marker: {
            color: '#dc3545'
        }
    };

    var trace2 = {
        x: ['level 1', 'level 2', 'level 3', 'level 4'],
        y: [data.LEVEL_1_LOSS_COUNT, data.LEVEL_2_LOSS_COUNT, data.LEVEL_3_LOSS_COUNT, data.LEVEL_4_LOSS_COUNT],
        type: 'bar',
        name: 'Loss trades',
        marker: {
            color: '#28a745'
        }
    };

    var c_data = [trace1, trace2];
    var layout = {barmode: 'group'};
    Plotly.newPlot('level_won_loss_counts_cht', c_data, layout);
}

function add_levels_won_loss_amount_graph(data) {
    var trace1 = {
        x: ['level 1', 'level 2', 'level 3', 'level 4'],
        y: [data.LEVEL_1_WON_AMOUNT, data.LEVEL_2_WON_AMOUNT, data.LEVEL_3_WON_AMOUNT, data.LEVEL_4_WON_AMOUNT],
        type: 'bar',
        name: 'Won trades amount',
        marker: {
            color: '#28a745'
        }
    };

    var trace2 = {
        x: ['level 1', 'level 2', 'level 3', 'level 4'],
        y: [data.LEVEL_1_LOSS_AMOUNT, data.LEVEL_2_LOSS_AMOUNT, data.LEVEL_3_LOSS_AMOUNT, data.LEVEL_4_LOSS_AMOUNT],
        type: 'bar',
        name: 'Loss trades amount',
        marker: {
            color: '#dc3545'
        }
    };

    var c_data = [trace1, trace2];
    var layout = {barmode: 'group'};
    Plotly.newPlot('level_won_loss_amount_cht', c_data, layout);
}

function fill_dashboard(data) {
    $("#all_won_count").html(data.all_won_count);
    $("#all_loss_count").html(data.all_lass_count);
    $("#all_won_amount").html(data.all_won_amount + " " + data.user_currency);
    $("#all_loss_amount").html(data.all_loss_amount + " " + data.user_currency);
}

function add_all_won_loss_graph(data) {
    var trace1 = {
        x: ['Count', 'Amount'],
        y: [data.all_won_amount, data.all_won_count],
        type: 'bar',
        name: 'Won',
        marker: {
            color: '#28a745'
        }
    };

    var trace2 = {
        x: ['Count', 'Amount'],
        y: [data.all_loss_amount, data.all_lass_count],
        type: 'bar',
        name: 'Loss',
        marker: {
            color: '#dc3545'
        }
    };

    var c_data = [trace1, trace2];
    var layout = {barmode: 'group'};
    Plotly.newPlot('total_won_loss_cht', c_data, layout);
}