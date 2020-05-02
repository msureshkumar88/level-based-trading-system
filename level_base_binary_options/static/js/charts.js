BASE_URL = "http://127.0.0.1:8000/";

WS_SERVER_URL = "http://localhost:8080/"
var chartModel = $('.chartModel');

var socket = "";

chartModel.on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);// Button that triggered the modal
    var transactionRef = button.data('transaction'); // Extract info from data-* attributes
    var tradeOwner = button.data('owner');
    socket = io.connect(WS_SERVER_URL);
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
            print(data)
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
    var payload = {user_id: tradeOwner, transaction_ref: transactionRef}
    socket.emit('get chart data', payload);

    socket.on('chart data', function (data) {

        // var dd = JSON.parse(data)

        // var close = data.close.split("")
        // for (x of close) {
        //     print(x)
        // }
        // socket.disconnect()
        drawGraph(data)
        print(data)
    });


});

chartModel.on('hidden.bs.modal', function () {
    socket.disconnect()
});

function drawGraph(response) {
    var close = JSON.parse(response.close)
    var timestamp = JSON.parse(response.timestamp)

    var data = [
        {
            x: timestamp,
            y: close,
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
                type: 'line',
                x0: response.end_date,
                y0: response.line_start,
                x1: response.end_date,
                y1: response.line_end,
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
                    color: 'rgb(128, 0, 128)',
                    width: 4,
                    dash: 'dot'
                }
            }


        ]

    };
    // var update = {
    // x:  [[timestamp]],
    // y: [[close]]
    // };
    Plotly.newPlot('fx-chart', data, layout);

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
