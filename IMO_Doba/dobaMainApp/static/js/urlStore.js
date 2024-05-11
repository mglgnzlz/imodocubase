//STORE URL CONFIGS IN LOCAL SESSION

$(document).ready(function() {
    // Check if there's any data in the local storage and set the form values
    if(localStorage.getItem('start_date')) {
      $('#start_date').val(localStorage.getItem('start_date'));
    }
    if(localStorage.getItem('end_date')) {
      $('#end_date').val(localStorage.getItem('end_date'));
    }
    if(localStorage.getItem('file_type')) {
      $('#file_type').val(localStorage.getItem('file_type'));
    }
  
    // When the form is submitted, store the form data in the local storage
    $('form').on('submit', function() {
      localStorage.setItem('start_date', $('#start_date').val());
      localStorage.setItem('end_date', $('#end_date').val());
      localStorage.setItem('file_type', $('#file_type').val());
    });
  });
  