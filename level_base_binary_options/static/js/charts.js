BASE_URL = "http://127.0.0.1:8000/";

WS_SERVER_URL = "http://localhost:8080/"
var chartModel = $('.chartModel');

var socket = "";

chartModel.on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);// Button that triggered the modal
    var transactionRef = button.data('transaction'); // Extract info from data-* attributes
    var tradeOwner = button.data('owner');

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
        drawGraph(data);
        print(data)
    });
}

var interval;

function loadChartLiveData(transactionRef, tradeOwner) {
    var payload = {user_id: tradeOwner, transaction_ref: transactionRef};
    socket = io.connect(WS_SERVER_URL);
    var cnt = 0;
    var requestTime = ""
    interval = setInterval(function () {
        payload['request_time'] = requestTime
        print(payload['request_time'])
        socket.emit('get chart data live', payload);

        if (++cnt === 100) {
            clearInterval(interval);
            socket.disconnect();
        }
    }, 1000);


    socket.on('chart data live', function (data) {
        // socket.disconnect()
        // drawGraph(data);
        print(data)
        var update = {
            x: [[data.timestamp]],
            y: [[data.close]]
        };
        requestTime = data.timestamp
        Plotly.extendTraces('fx-chart', update, [0])
    });
}

function loadSingleTrade(transactionRef, tradeOwner) {
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

        }
    });
}

chartModel.on('hidden.bs.modal', function () {
    clearInterval(interval);
    socket.disconnect()
});

function drawGraph(response) {
    var close = JSON.parse(response.close)
    var timestamp = JSON.parse(response.timestamp)
    print(timestamp[0])
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
    layout['shapes'] = getLayoutByTradeType(response)

    // var update = {
    // x:  [[timestamp]],
    // y: [[close]]
    // };
    Plotly.newPlot('fx-chart', data, layout);
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

function getLayoutByTradeType(response) {
    if (response.trade_type === "levels") {
        var ranges = JSON.parse(response.levels_price)
        var levelMap = []

        levelMap.push({
            type: 'line',
            x0: response.start_time,
            y0: ranges[0].range[0],
            x1: response.end_date,
            y1: ranges[0].range[0],
            line: {
                color: 'rgb(250, 37, 37)',
                width: 4,
                dash: 'dot'
            }
        });
        ranges.forEach(function (item, index) {
            // print(item.range)
            // print(index)
            levelMap.push({
                type: 'line',
                x0: response.start_time,
                y0: item.range[1],
                x1: response.end_date,
                y1: item.range[1],
                line: {
                    color: 'rgb(128, 0, 128)',
                    width: 4,
                    dash: 'dot'
                }
            })
        });

        print(levelMap)
        return levelMap
    }
    //todo: fix trade shapes for binary trading
    return [
        {
            type: 'line',
            x0: response.start_time,
            y0: response.line_start,
            x1: response.start_time,
            y1: response.line_end,
            line: {
                color: 'rgb(55, 128, 191)',
                width: 3
            },
        },
        {
            type: 'line', x0: response.end_date, y0: response.line_start, x1: response.end_date, y1: response.line_end,
            line: {
                color: 'rgb(55, 128, 191)',
                width: 3,
                dash: 'dot'
            },
        },
        {
            type: 'line',
            x0: response.start_time,
            y0: response.start_price,
            x1: response.end_date,
            y1: response.start_price,
            line: {
                color: 'rgb(250, 37, 37)',
                width: 4,
                dash: 'dot'
            }
        }


    ]
}

//https://plotly.com/javascript/shapes/
//https://plotly.com/javascript/setting-graph-size/
//https://plotly.com/javascript/time-series/
//https://simpleisbetterthancomplex.com/tutorial/2016/08/29/how-to-work-with-ajax-request-with-django.html
//https://plotly.com/javascript/streaming/
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
    print(Math.random())
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
function print(val) {
    console.log(val)
}


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
