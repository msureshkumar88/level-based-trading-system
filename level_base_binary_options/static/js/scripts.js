//binary options trade creations page /account
$('.binaryConfirmationModel').on('show.bs.modal', function (event) {
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

