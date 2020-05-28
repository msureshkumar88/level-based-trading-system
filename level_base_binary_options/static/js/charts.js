BASE_URL = "http://127.0.0.1:8000/";

WS_SERVER_URL = "http://localhost:8080/"
var chartModel = $('.chartModel');

var socket = "";

var chart_timestamps = [];
var char_price = [];
chartModel.on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);// Button that triggered the modal
    // var transactionRef = button.data('transaction'); // Extract info from data-* attributes
    // var tradeOwner = button.data('owner');
    // var transactionRef = $('#trade_id').val()
    // var tradeOwner = $('#user_id').val()
    var transactionRef = $('input[name="trade_id"]').val();
    var tradeOwner = $('input[name="user_id"]').val();

    if (transactionRef === "" && tradeOwner === "") {
        transactionRef = button.data('transaction'); // Extract info from data-* attributes
        tradeOwner = button.data('owner');
    }
    $('#join').val(transactionRef);
    $('#close_binary_trade').val(transactionRef);

    console.log(transactionRef)
    console.log(tradeOwner)
    chart_timestamps = [];
    loadSingleTrade(transactionRef, tradeOwner);
    loadChartHistoryData(transactionRef, tradeOwner);
    // loadChartLiveData(transactionRef, tradeOwner);


});


function loadChartHistoryData(transactionRef, tradeOwner) {
    var payload = {user_id: tradeOwner, transaction_ref: transactionRef};
    socket = io.connect(WS_SERVER_URL);
    socket.emit('get chart data history', payload);

    socket.on('chart data history', function (data) {
        // socket.disconnect()
        chart_timestamps.push(...JSON.parse(data.timestamp))
        char_price.push(...JSON.parse(data.close))

        // console.log(chart_timestamps)
        console.log('---------------')
        console.log(data)
        drawGraph(data);
        if (data.status !== "finished") {
            //todo: fix if history data is not available live data not loading issue
            loadChartLiveData(transactionRef, tradeOwner)
        }
        console.log(data)
    });
}

var interval_trade;

var traders_joined_area = $('#traders_joined_area');
var level_selected_area = $('#level_selected_area');

var level_join_area = $('#level_join_area')
var binary_close_area = $('#binary_close_area')

traders_joined_area.hide();
level_selected_area.hide();

level_join_area.hide();
binary_close_area.hide()

function loadChartLiveData(transactionRef, tradeOwner) {
    var payload = {user_id: tradeOwner, transaction_ref: transactionRef};
    socket = io.connect(WS_SERVER_URL);
    var cnt = 0;

    interval_trade = setInterval(function () {
        socket.emit('get chart data live', payload);

        // if (++cnt === 100) {
        //     clearInterval(interval);
        //     socket.disconnect();
        // }
    }, 500);


    socket.on('chart data live', function (data) {
            // socket.disconnect()
            // drawGraph(data);
            console.log(data)
            console.log(Object.keys(data).length)
            traders_joined_area.hide();
            level_selected_area.hide();
            // level_join_area.hide();
            // binary_close_area.hide();

            if (data.timestamp !== "" && data.close !== "") {
                if (data.status === "finished") {
                    // if (!chart_timestamps.includes(data.timestamp)) {
                    var update = {
                        x: [[data.timestamp]],
                        y: [[data.close]]
                    };

                    Plotly.extendTraces('fx-chart', update, [0])
                    chart_timestamps.push(data.timestamp)
                    char_price.push(data.close)
                    var update_layout = {

                        shapes: getShapesByTradeType(data)
                    };
                    Plotly.relayout('fx-chart', update_layout);
                    $('#close-price').html(data.closing_price == null ? data.closing_price : data.closing_price.toFixed(5));
                    $('#outcome').html(S(data.outcome).capitalize().s);
                    // }
                    clearInterval(interval_trade);
                    socket.disconnect();
                }
                if (!chart_timestamps.includes(data.timestamp) && data.status !== "finished") {
                    var update = {
                        x: [[data.timestamp]],
                        y: [[data.close]]
                    };

                    Plotly.extendTraces('fx-chart', update, [0])
                    chart_timestamps.push(data.timestamp)
                    char_price.push(data.close)
                    var update_layout = {

                        shapes: getShapesByTradeType(data)
                    };
                    Plotly.relayout('fx-chart', update_layout);

                }
            }
            if (data.trade_type === 'levels') {
                traders_joined_area.show();
                level_selected_area.show();
                $('#level_selected').html(data.level_selected);
                $('#traders_joined').html(data.user_count);
                binary_close_area.hide();

                if (data.status !== "finished") {
                    level_join_area.show();
                    var join_options = $('#join-options');
                    if ($("#join-options option").length - 1 !== data.available_levels.length) {
                        var join_options_list = "<option value=''>Select level</option>";
                        data.available_levels.forEach(function (item, index) {
                            join_options_list = join_options_list + '<option>' + item + '</option>';
                        });

                        join_options.html(join_options_list)
                    }
                }


            } else {
                traders_joined_area.hide();
                level_selected_area.hide();
                level_join_area.hide();
                // binary_close_area.show()
            }

            if (data.trade_type === 'binary') {
                if (data.status === "finished") {
                    binary_close_area.hide()
                } else {
                    binary_close_area.show()
                }
            }

        }
    )
    ;
}

function loadSingleTrade(transactionRef, tradeOwner) {
    traders_joined_area.hide();
    level_selected_area.hide();
    level_join_area.hide();
    binary_close_area.hide()
    $.ajax({
        url: BASE_URL + 'account/get-transaction',
        data: {
            'transaction_ref': transactionRef,
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'trade_owner': tradeOwner
        },
        dataType: 'json',
        method: 'POST',
        success: function (data) {
            data = data.data[0];
            $('#transaction-id').html(data.transaction_ref);
            $('#contract_type').html(S(data.contract_type).capitalize().s);
            $('#purchase-type').html(S(data.purchase_type).capitalize().s);
            $('#start-time').html(moment(data.start_time, "YYYY-MM-DD kk:mm:ss").format("YYYY-MM-DD kk:mm:ss"));
            $('#end-time').html(moment(data.end_time, "YYYY-MM-DD kk:mm:ss").format("YYYY-MM-DD kk:mm:ss"));
            $('#start-price').html(data.staring_price.toFixed(5));
            $('#close-price').html(data.closing_price == null ? data.closing_price : data.closing_price.toFixed(5));
            $('#amount').html(S(data.amount).toFloat().toFixed(2) + " " + data.user_currency.toUpperCase());
            $('#outcome').html(S(data.outcome).capitalize().s);
            if (data.contract_type === 'levels') {
                traders_joined_area.show();
                level_selected_area.show();
                $('#level_selected').html(data.selected_level);
                $('#traders_joined').html(data.user_count);
                binary_close_area.hide();

                if (data.status !== "finished") {
                    level_join_area.show();
                    var join_options = $('#join-options');
                    var join_options_list = "<option value=''>Select level</option>";
                    data.available_levels.forEach(function (item, index) {
                        join_options_list = join_options_list + '<option>' + item + '</option>';
                    });
                    join_options.html(join_options_list);
                }
            } else {
                traders_joined_area.hide();
                level_selected_area.hide();
                level_join_area.hide();
                // binary_close_area.show()
            }

            if (data.trade_type === 'binary') {
                if (data.status === "finished") {
                    binary_close_area.hide()
                } else {
                    binary_close_area.show()
                }
            }
        }
    });
}

chartModel.on('hidden.bs.modal', function () {
    clearInterval(interval_trade);
    socket.disconnect()
});

function drawGraph(response) {
    var close = JSON.parse(response.close)
    var timestamp = JSON.parse(response.timestamp)
    var data = [
        {
            x: timestamp,
            y: close,
            type: 'lines'
        }
    ];
    var layout = {
        autosize: false,
        width: 780,
        height: 600,
        yaxis: {
            automargin: true,
        },
        xaxis: {
            title: 'Y-axis Title',
        },
    };
    layout['shapes'] = getShapesByTradeType(response);
    Plotly.newPlot('fx-chart', data, layout);

    // var update = {
    // x:  [[timestamp]],
    // y: [[close]]
    // };

    // var old = {
    //         x: [[timestamp[0],timestamp[1],timestamp[2]]],
    //         y: [[close[0],close[1],close[2]]]
    //     };
    // var old = {
    //         x: [timestamp],
    //         y: [close]
    //     };
    // Plotly.extendTraces('fx-chart', old, [0])
    // var update = {
    //         x: [["2020-01-03 00:01:00","2020-01-03 00:02:00","2020-01-03 00:03:00"]],
    //         y: [[1.11704,1.11708,1.11711]]
    //     };
    //
    // Plotly.extendTraces('fx-chart', update, [0])

}

function getShapesByTradeType(response) {

    if (response.trade_type === "levels") {
        var ranges = JSON.parse(response.levels_price);
        var levelMap = [];
        //level gap lines
        levelMap.push({
            type: 'line',
            x0: chart_timestamps[0],
            y0: ranges[0].range[0],
            x1: chart_timestamps[chart_timestamps.length - 1],
            y1: ranges[0].range[0],
            line: {
                color: 'rgb(250, 37, 37)',
                width: 4,
                dash: 'dot'
            }
        });
        ranges.forEach(function (item, index) {
            levelMap.push({
                type: 'line',
                x0: chart_timestamps[0],
                y0: item.range[1],
                x1: chart_timestamps[chart_timestamps.length - 1],
                y1: item.range[1],
                line: {
                    color: 'rgb(128, 0, 128)',
                    width: 4,
                    dash: 'dot'
                }
            })
        });

        console.log(response.status)
        //trade end line
        if (response.status === "finished") {
            levelMap.push(
                {
                    type: 'line',
                    x0: chart_timestamps[chart_timestamps.length - 1],
                    y0: char_price[char_price.length - 1] - 0.0001,
                    x1: chart_timestamps[chart_timestamps.length - 1],
                    y1: char_price[char_price.length - 1] + 0.0001,
                    line: {
                        color: 'rgb(75, 166, 63)',
                        width: 3,
                    },
                }
            )
        }
        //trade start line
        levelMap.push(
            //         {
            //   type: 'circle',
            //   xref: 'x',
            //   yref: 'y',
            //   fillcolor: 'rgba(50, 171, 96, 0.1)',
            //   x0: response.start_time,
            //   y0: response.start_price,
            //   x1: chart_timestamps[15],
            //   y1: response.start_price+0.00001,
            //   line: {
            //     color: 'rgba(50, 171, 96, 1)'
            //   }
            // }

            {
                type: 'line',
                x0: chart_timestamps[0],
                y0: response.start_price - 0.0001,
                x1: chart_timestamps[0],
                y1: response.start_price + 0.0001,
                line: {
                    color: 'rgb(0, 191, 230)',
                    width: 3,
                },
            }
        );
        return levelMap
    }
    //todo: fix trade shapes for binary trading
    if (response.trade_type === "binary") {
        var levelMap = [
            //start line
            {
                type: 'line',
                x0: chart_timestamps[0],
                y0: response.start_price - 0.0001,
                x1: chart_timestamps[0],
                y1: response.start_price + 0.0001,
                line: {
                    color: 'rgb(55, 128, 191)',
                    width: 3
                },
            },
            {
                type: 'line',
                x0: chart_timestamps[0],
                y0: response.start_price,
                x1: chart_timestamps[chart_timestamps.length - 1],
                y1: response.start_price,
                line: {
                    color: 'rgb(250, 37, 37)',
                    width: 4,
                    dash: 'dot'
                }
            }
        ];

        if (response.status === "finished") {
            levelMap.push(
                {
                    type: 'line',
                    x0: chart_timestamps[chart_timestamps.length - 1],
                    y0: char_price[char_price.length - 1] - 0.0001,
                    x1: chart_timestamps[chart_timestamps.length - 1],
                    y1: char_price[char_price.length - 1] + 0.0001,
                    line: {
                        color: 'rgb(75, 166, 63)',
                        width: 3,
                    },
                }
            )
        }
        return levelMap
    }

    // return [
    //     {
    //         type: 'line',
    //         x0: response.start_time,
    //         y0: response.line_start,
    //         x1: response.start_time,
    //         y1: response.line_end,
    //         line: {
    //             color: 'rgb(55, 128, 191)',
    //             width: 3
    //         },
    //     },
    //     {
    //         type: 'line', x0: response.end_date, y0: response.line_start, x1: response.end_date, y1: response.line_end,
    //         line: {
    //             color: 'rgb(55, 128, 191)',
    //             width: 3,
    //             dash: 'dot'
    //         },
    //     },
    //     {
    //         type: 'line',
    //         x0: response.start_time,
    //         y0: response.start_price,
    //         x1: response.end_date,
    //         y1: response.start_price,
    //         line: {
    //             color: 'rgb(250, 37, 37)',
    //             width: 4,
    //             dash: 'dot'
    //         }
    //     }
    //
    //
    // ]
}

var interval
var chart_currency_ele = $("#chart_currency");
var timeframe_ele = $("#timeframe");
var chart_type_ele = $("#chart_type");
var price_type_ele = $("#price_type");

var socket_chart = "";

if ($("#forex-chart").length) {
    load_chart_history("EUR/USD", "ticks", "close", "line")
}

chart_currency_ele.change(function () {
    if (socket_chart !== "") {
        socket_chart.disconnect();
        clearInterval(interval);
    }
    var chart_currency = $(this).val();
    var timeframe = timeframe_ele.val();
    var price_type = price_type_ele.val();
    var chart_type = chart_type_ele.val();

    load_chart_history(chart_currency, timeframe, price_type, chart_type)
});
timeframe_ele.change(function () {
    if (socket_chart !== "") {
        socket_chart.disconnect();
        clearInterval(interval);
    }
    var timeframe = $(this).val();
    var chart_currency = chart_currency_ele.val();
    var price_type = price_type_ele.val();
    var chart_type = chart_type_ele.val();
    load_chart_history(chart_currency, timeframe, price_type, chart_type)
});

price_type_ele.change(function () {
    if (socket_chart !== "") {
        socket_chart.disconnect();
        clearInterval(interval);
    }
    var price_type = $(this).val();
    var timeframe = timeframe_ele.val();
    var chart_currency = chart_currency_ele.val();
    var chart_type = chart_type_ele.val();
    load_chart_history(chart_currency, timeframe, price_type, chart_type)
})

chart_type_ele.change(function () {
    if (socket_chart !== "") {
        socket_chart.disconnect();
        clearInterval(interval);
    }
    var chart_type = $(this).val();
    var timeframe = timeframe_ele.val();
    var chart_currency = chart_currency_ele.val();
    var price_type = price_type_ele.val();
    load_chart_history(chart_currency, timeframe, price_type, chart_type)

})
var hist_timestamp = [];
var hist_price_open = [];
var hist_price_close = [];
var hist_price_high = [];
var hist_price_low = [];

function load_chart_history(chart_currency, timeframe, price_type, chart_type) {
    hist_timestamp = [];
    hist_price_open = [];
    hist_price_close = [];
    hist_price_high = [];
    hist_price_low = [];
    $.ajax({
        url: BASE_URL + 'account/get-chart-data',
        data: {
            'timeframe': timeframe,
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'chart_currency': chart_currency,
            'price_type': price_type,
            'chart_type': chart_type,
        },
        dataType: 'json',
        method: 'POST',
        success: function (data) {
            console.log(data.data)
            if (data.status) {
                var c_data = data.data
                add_chart(c_data)

                if ("timestamp" in c_data) {
                    hist_timestamp.push(...JSON.parse(c_data.timestamp))
                }
                if ("open" in c_data) {
                    hist_price_open.push(...JSON.parse(c_data.open))
                }
                if ("close" in c_data) {
                    hist_price_close.push(...JSON.parse(c_data.close))
                }
                if ("high" in c_data) {
                    hist_price_high.push(...JSON.parse(c_data.high))
                }
                if ("low" in c_data) {
                    hist_price_low.push(...JSON.parse(c_data.low))
                }

                load_live_chart(chart_currency, timeframe, price_type, chart_type)
            }

        }
    });

}

function load_live_chart(chart_currency, timeframe, price_type, chart_type) {

    var payload = {}
    payload = {
        chart_currency: chart_currency,
        timeframe: timeframe,
        price_type: price_type,
        chart_type: chart_type
    };
    socket_chart = io.connect(WS_SERVER_URL);
    interval = setInterval(function () {
        socket_chart.emit('live forex data', payload);

    }, 500);

    socket_chart.on('forex data live', function (data) {
        var c_data = data.data


        if (chart_type === "line") {
            update_line_chart(c_data)
        }
        if (chart_type === "candlestick") {
            update_candlestick_chart(c_data)
        }
        // console.log(hist_price_open)
        // console.log(hist_price_close)
        // console.log(hist_price_high)
        // console.log(hist_price_low)

    });

}

//https://plotly.com/javascript/axes/
function add_chart(data) {
    var chart_type = chart_type_ele.val();
    var timeframe = timeframe_ele.val();
    var price_type = price_type_ele.val();

    if (chart_type === "candlestick" && timeframe !== "ticks") {
        var trace1 = {

            x: JSON.parse(data.timestamp),
            close: JSON.parse(data.close),
            decreasing: {line: {color: '#7F7F7F'}},
            high: JSON.parse(data.high),
            increasing: {line: {color: '#17BECF'}},
            line: {color: 'rgba(31,119,180,1)'},
            low: JSON.parse(data.low),
            open: JSON.parse(data.open),
            type: 'candlestick',
            xaxis: 'x',
            yaxis: 'y'
        };

        var chart_data = [trace1];

        var layout = {
            dragmode: 'zoom',
            margin: {
                r: 10,
                t: 25,
                b: 40,
                l: 60
            },
            showlegend: false,
            xaxis: {
                autorange: true,
                domain: [0, 1],
                // range: ['2017-01-03 12:00', '2017-02-15 12:00'],
                // rangeslider: {range: ['2017-01-03 12:00', '2017-02-15 12:00']},
                title: 'Date',
                type: 'date'
            },
            yaxis: {
                // autotick: false,
                // dtick: 0.00030,
                autorange: true,
                domain: [0, 1],
                // range: [114.609999778, 137.410004222],
                type: 'linear'
            }
        };

        Plotly.newPlot('forex-chart', chart_data, layout);
    }

    if (chart_type === "line") {
        var trace1 = {
            type: "scatter",
            mode: "lines",
            name: 'AAPL High',
            x: JSON.parse(data.timestamp),
            line: {color: '#17BECF'}
        };

        if (price_type === "close") {
            trace1['y'] = JSON.parse(data.close)
        }
        if (price_type === "open") {
            trace1['y'] = JSON.parse(data.open)
        }
        if (price_type === "high") {
            trace1['y'] = JSON.parse(data.high)
        }
        if (price_type === "low") {
            trace1['y'] = JSON.parse(data.low)
        }

        var data = [trace1];

        var layout = {
            title: 'Basic Time Series',
        };

        Plotly.newPlot('forex-chart', data, layout);
    }

}

function update_line_chart(data) {
    console.log(data)
    var update = {};
    if (hist_timestamp.includes(data.timestamp)) {
        var update_required = false;

        var time_index = hist_timestamp.indexOf(data.timestamp);
        if ("open" in data) {
            if (data.open !== hist_price_open[time_index]) {
                hist_price_open[time_index] = data.open;
                update_required = true;
                update = {
                    x: [[data.timestamp]],
                    y: [[data.open]]
                };
            }
        }
        if ("close" in data) {
            if (data.close !== hist_price_close[time_index]) {
                hist_price_close[time_index] = data.close;
                update_required = true;
                update = {
                    x: [[data.timestamp]],
                    y: [[data.close]]
                };
            }
        }
        if ("high" in data) {
            if (data.high !== hist_price_high[time_index]) {
                hist_price_high[time_index] = data.high;
                update_required = true;
                update = {
                    x: [[data.timestamp]],
                    y: [[data.high]]
                };
            }
        }
        if ("low" in data) {
            if (data.low !== hist_price_low[time_index]) {
                hist_price_low[time_index] = data.low;
                update_required = true;
                update = {
                    x: [[data.timestamp]],
                    y: [[data.low]]
                };
            }
        }
        if (update_required) {
            Plotly.extendTraces('forex-chart', update, [0])
        }


    }
    if (!hist_timestamp.includes(data.timestamp)) {

        update = {
            x: [[data.timestamp]],
        };

        hist_timestamp.push(data.timestamp);
        if ("open" in data) {
            hist_price_open.push(data.open);
            update['y'] = [[data.open]]
        }
        if ("close" in data) {
            hist_price_close.push(data.close);
            update['y'] = [[data.close]]
        }
        if ("high" in data) {
            hist_price_high.push(data.high);
            update['y'] = [[data.high]]
        }
        if ("low" in data) {
            hist_price_low.push(data.low);
            update['y'] = [[data.low]]
        }
        Plotly.extendTraces('forex-chart', update, [0])
    }
}

function update_candlestick_chart(data) {

    var update = {};
    if (hist_timestamp.includes(data.timestamp)) {
        var update_required = false;
        var time_index = hist_timestamp.indexOf(data.timestamp);

        if (data.open !== hist_price_open[time_index]) {
            hist_price_open[time_index] = data.open;
            update_required = true
        }
        if (data.close !== hist_price_close[time_index]) {
            hist_price_close[time_index] = data.close;
            update_required = true
        }
        if (data.high !== hist_price_high[time_index]) {
            hist_price_high[time_index] = data.high;
            update_required = true
        }
        if (data.low !== hist_price_low[time_index]) {
            hist_price_low[time_index] = data.low;
            update_required = true
        }

        if (update_required) {
            update = {
                x: [[data.timestamp]],
                close: [[data.close]],
                high: [[data.high]],
                low: [[data.low]],
                open: [[data.open]],
            };
            Plotly.extendTraces('forex-chart', update, [0])
        }

    }
    if (!hist_timestamp.includes(data.timestamp)) {
        console.log(data)
        hist_timestamp.push(data.timestamp);
        hist_price_open.push(data.open);
        hist_price_close.push(data.close);
        hist_price_high.push(data.high);
        hist_price_low.push(data.low);

        update = {
            x: [[data.timestamp]],
            close: [[data.close]],
            high: [[data.high]],
            low: [[data.low]],
            open: [[data.open]],
        };
        Plotly.extendTraces('forex-chart', update, [0])
    }
}

$('#join').click(function () {
    var transaction_id = $(this).val();
    var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();
    var selected_level = $("#join-options option:selected").val();

    $.ajax({
        url: BASE_URL + 'account/join-trade',
        data: {
            'csrfmiddlewaretoken': csrfmiddlewaretoken,
            'trans': transaction_id,
            'selected_level': selected_level,

        },
        dataType: 'json',
        method: 'POST',
        success: function (data) {
            console.log(data)

            var message = $("#action-message")
            message.html("")
            if (data.status) {
                message.html("<span class='text text-success'>" + data.message[0] + "</span>")
            } else {
                var err = "<span class='text text-danger'>";

                data.message.forEach(function (item, index) {
                    console.log(item);
                    err = err + item + ", "
                });

                err = err + "</span>"

                message.html(err)
            }
        }
    });

});
$('#close_binary_trade').click(function () {
    var transaction_id = $(this).val();
    var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();


    $.ajax({
        url: BASE_URL + 'account/close-order',
        data: {
            'csrfmiddlewaretoken': csrfmiddlewaretoken,
            'transaction_id': transaction_id,
        },
        dataType: 'json',
        method: 'POST',
        success: function (data) {
            console.log(data)

            var message = $("#action-message")
            message.html("")
            if (data.status) {
                message.html("<span class='text text-success'>" + data.message[0] + "</span>")
            } else {
                var err = "<span class='text text-danger'>";

                data.message.forEach(function (item, index) {
                    console.log(item);
                    err = err + item + ", "
                });

                err = err + "</span>"

                message.html(err)
            }
        }
    });
});
//https://plotly.com/javascript/shapes/
//https://plotly.com/javascript/setting-graph-size/
//https://plotly.com/javascript/time-series/
//https://simpleisbetterthancomplex.com/tutorial/2016/08/29/how-to-work-with-ajax-request-with-django.html
//https://plotly.com/javascript/streaming/
//https://plotly.com/javascript/spc-control-charts/
/*
var data = [
    {
        x: ['2013-10-04 22:23:00', '2013-11-04 22:23:00', '2013-12-04 22:23:00'],
        y: [1, 3, 6],
        type: 'scatter'
    }
];
var layout = {
    autosize: false,
    width: 780,
    height: 600,
    yaxis: {
        automargin: true,
    },
    xaxis: {
        title: 'Y-axis Title',
    },
    shapes: [
        {
            type: 'line',
            x0: '2013-10-04 22:23:00',
            y0: 0,
            x1: '2013-10-04 22:23:00',
            y1: 12,
            line: {
                color: 'rgb(55, 128, 191)',
                width: 3
            },
        },
        {
            type: 'line',
            x0: '2013-12-04 22:23:00',
            y0: 0,
            x1: '2013-12-04 22:23:00',
            y1: 12,
            line: {
                color: 'rgb(55, 128, 191)',
                width: 3,
                dash: 'dot'
            },
        },
        {
            type: 'line',
            x0: '2013-10-04 22:23:00',
            y0: 4,
            x1: '2013-12-04 22:23:00',
            y1: 4,
            line: {
                color: 'rgb(128, 0, 128)',
                width: 4,
                dash: 'dot'
            }
        }


    ]


};
Plotly.newPlot('fx-chart', data, layout);
*/

/*
function rand() {
    console.log(Math.random())
  return Math.random();
}

Plotly.newPlot('fx-chart', [{
  y: [1,2,3].map(rand),
  mode: 'lines',
  line: {color: '#80CAF6'}
}]);

var cnt = 0;

var interval = setInterval(function() {

  Plotly.extendTraces('fx-chart', {
    y: [[rand()]]
  }, [0])

  if(++cnt === 100) clearInterval(interval);
}, 300);
*/

function rand() {
    return Math.random();
}

// var time = new Date();
//
// var data = [{
//   x: [time],
//   y: [rand()],
//   mode: 'lines',
//   line: {color: '#80CAF6'}
// }]
//
//
// Plotly.newPlot('fx-chart', data);
//
// var cnt = 0;
//
// var interval = setInterval(function() {
//
//   var time = new Date();
//
//   var update = {
//   x:  [[time]],
//   y: [[rand()]]
//   }
//
//   Plotly.extendTraces('fx-chart', update, [0])
//
//   if(++cnt === 100) clearInterval(interval);
// }, 1000);
// function print(val) {
//     console.log(val)
// }


// socket.on('connect', onConnect());

// socket.on('connect', onConnect());
// socket.on('chat_message', function () {
//     socket.emit('my custom event', {"sid": "121212121212", "data": "chat_message"});
// });
// socket.on('disconnect', function () {
//     socket.emit('my custom event', {"sid": "11111", "data": "user is disconnected"});
// });
//
// socket.on('connect', function () {
//     socket.emit('my custom event', {"sid": "11111", "data": "user is connected"});
// })
// socket.emit('my custom event', {"sid": "11111", "data": "user sent a new message"});
//
// socket.emit('chat_message', {"sid": "121212121212", "data": "chat_message"});
// setInterval(function () {
//     socket.emit('chat_message', {"sid": "121212121212", "data": "chat_message"});
// }, 1000);
//
// // setTimeout(function(){
// //     socket.emit('chat_message', {"sid": "121212121212", "data": "chat_message"});
// // }, 1000);
//
// socket.on('reply', function (data) {
//     console.log(data)
// })
// socket.on('new_server_reply', function (data) {
//     console.log(data)
// })
//
// socket.on('my event', function (data) {
//     console.log(data)
// })

