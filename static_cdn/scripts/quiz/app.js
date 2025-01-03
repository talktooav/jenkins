$(document).ready(function() {
  $("#groupsubmitForm").submit(function(e) {
    $('.form-group').removeClass('has-error'); 
    $('.error').remove(); 
    $('#msg-group').html('');
	$.ajax({
            type: 'POST',
             url: $(this).attr('action'),
            data: new FormData(this), // our data object
         enctype: 'multipart/form-data',
           async: false,
     contentType: false,
           cache: false,
     processData: false,
        dataType: 'json', 
      beforeSend: function( xhr ) {
		$(".loading-overlay").show();
		$('#groups_submit').attr('disabled', true);
      }
    })
    .done(function(response) {
       $('.loading-overlay').fadeOut("slow");
       var focus_key = '';
       if (response.success) { 
           var focus_key = 'msg';
           $('#groupsubmitForm')[0].reset(); 
           $('#msg-group').append('<div class="alert alert-success text-success">'+response.msg+'</div>');
           setTimeout(function() {
              window.location.href = response.redirect_url;
           }, 3000);
       } 
       else if (response.success==false) {  
          var i = 0;
          if ( (response.msg) && (response.msg!=undefined) ) { 
             $('#msg-group').append('<div class="alert alert-danger text-danger error">'+response.msg+'</small>');
             focus_key = 'msg';
          }
          else {
            $.each(JSON.parse(response.errors), function(key, value) { 
              if (i==0)
                 focus_key = key;
              
              $('#'+key+'-group').addClass('has-error'); // add the error class to show red input
              $('#'+key+'-group').append('<small class="error">' + value[0].message + '</small>');
              ++i;
            }); 
            //~ $("input[name='mdm_token']").val(response.errors.get_csrf_hash); 
          }
          //~ $('html, body').animate({ 
            //~ scrollTop:$('#'+focus_key+'-group').offset().top - ($(window).height() / 2)
          //~ }, 500, function() { 
             //~ $('#'+focus_key+'-group').focus();
          //~ });
        }
    });
    event.preventDefault();

  });
   
});

var today = new Date();
$('#start_date').on('click', function() {
    $("#start_date").datetimepicker({
      format: 'YYYY-MM-DD',
      minDate:today,
      autoHide: true,
      widgetPositioning: {
       horizontal: 'right',
       vertical: 'bottom'
      }
    });
});
//~ var plus_day = today.setDate(today.getDate() + 1)
$('#end_date').on('click', function() {
    var start_date = $('#start_date').data('date');
    start_date = new Date(start_date);
    var plus_start_date = start_date.setDate(start_date.getDate() + 1)
    $("#end_date").datetimepicker({
      format: 'YYYY-MM-DD',
      minDate:plus_start_date  ,
      autoHide: true,
      widgetPositioning: {
       horizontal: 'right',
       vertical: 'bottom'
      }
    });
    
});
$('#result_date').on('click', function() {
    var result_date = $('#end_date').data('date');
    result_date = new Date(result_date);
    var plus_day = result_date.setDate(result_date.getDate() + 1)
    $("#result_date").datetimepicker({
      format: 'YYYY-MM-DD',
      minDate:plus_day,
      autoHide: true,
      widgetPositioning: {
       horizontal: 'right',
       vertical: 'bottom'
      }
    });
});
