$(document).ready(function(){
  $.ajax({
    type: "GET",
    url: "/rolls",
    success: function(data) {
      $.each(data, function(contract, details) {
        $("#rolls_status tbody").append(`
          <tr><td>${contract}</td>
          <td>${details['status']}</td>
          <td>${details['roll_expiry']}</td>
          <td>${details['carry_expiry']}</td>
          <td>${details['price_expiry']}</td>
          <td>${details['contract_labels'][0]}</td>
          </tr>`);
      }
      );
    }
  });
});

