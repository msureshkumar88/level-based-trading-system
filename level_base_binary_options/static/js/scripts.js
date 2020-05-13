//binary options trade creations page /account and /levels

$('.tradeConfirmationModel').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget) // Button that triggered the modal
    var action = button.data('action') // Extract info from data-* attributes
    var purchaseBtn = $('#purchase')
    purchaseBtn.removeClass()
    purchaseBtn.addClass('btn btn-normal')
    if (action === "Buy") {
        purchaseBtn.addClass('btn btn-primary')
    } else {
        purchaseBtn.addClass('btn btn-danger')
    }

    purchaseBtn.prop('value', action);
});

var start_later_area = $(".start_later_area")
start_later_area.hide()
$("#start_now_chk").click(function () {
    start_later_area.fadeOut()

});

$("#start_later_chk").click(function () {
    start_later_area.fadeIn()
});

var time_to_close = $("#time_to_close");
var duration_area = $(".duration_area");
var end_time_area = $(".end_time_area");

duration_area.hide();
end_time_area.hide();
time_to_close.change(function () {
    var val = time_to_close.val();
    if (val === "duration") {
        duration_area.show()
        end_time_area.hide()
    }
    else if (val === "end_time") {
        end_time_area.show()
        duration_area.hide()
    } else {
        duration_area.hide();
        end_time_area.hide();
    }


});

$(".binary-btn").click(function () {
    // console.log($("#binary-form").serialize())
    $.ajax({
        url: BASE_URL + 'account/save_binary',
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'start': $('input[name=start]:checked').val(),
            'start_date': $('input[name="start_date"]').val(),
            'start_time': $('input[name="start_time"]').val(),
            'currency': $("#currency option:selected").val(),
            'time_to_close': $("#time_to_close option:selected").val(),
            'time_slot': $("#time_slot option:selected").val(),
            'time_count': $('input[name="time_count"]').val(),
            'end_date': $('input[name="end_date"]').val(),
            'end_time': $('input[name="end_time"]').val(),
            'amount': $('input[name="amount"]').val(),
            'purchase': $(this).val(),
        },
        dataType: 'json',
        method: 'POST',
        success: function (data) {

            if (!data.status) {
                var err = "<div class='alert alert-danger'>";
                err = err + "<ul>"
                data.message.forEach(function (item, index) {
                    console.log(item)
                    err = err + "<li>" + item + "</li>"
                });
                err = err + "</ul>"
                err = err + "</div>"
                $("#messages").html(err)
            }
            if (data.status) {

            }
        }
    });
    // console.log( {
    //         'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
    //         'start': $('input[name=start]:checked').val(),
    //         'start_date': $('input[name="start_date"]').val(),
    //         'start_time': $('input[name="start_time"]').val(),
    //         'currency': $( "#currency option:selected" ).val(),
    //         'time_to_close': $("#time_to_close option:selected" ).val(),
    //         'time_slot': $( "#time_slot option:selected" ).val(),
    //         'time_count': $('input[name="time_count"]').val(),
    //         'end_date': $('input[name="end_date"]').val(),
    //         'end_time': $('input[name="end_time"]').val(),
    //         'amount': $('input[name="amount"]').val(),
    //         'purchase': $(this).val(),
    //     })
})

