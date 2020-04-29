$('.binaryConfirmationModel').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget) // Button that triggered the modal
    var action = button.data('action') // Extract info from data-* attributes
    var purchaseBtn = $('#purchase')
    purchaseBtn.removeClass()
    purchaseBtn.addClass('btn btn-normal')
    if (action === "Buy"){
        purchaseBtn.addClass('btn btn-primary')
    }else {
        purchaseBtn.addClass('btn btn-danger')
    }

    purchaseBtn.prop('value', action);
});

