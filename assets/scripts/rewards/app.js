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
var today = new Date();
$('#from_date').on('click', function() {
    $("#from_date").datetimepicker({
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
    var from_date = $('#from_date').data('date');
    from_date = new Date(from_date);
    var plus_from_date = from_date.setDate(from_date.getDate() + 1)
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
  

   $('#deleteall').click(function() {
     var seln_count = $('input.list_item:checked').length;
     if (seln_count==0)
        alert('select records to delete!');
     else {
        $.ajax({
               url:"{{ request.path }}delete",
               type: 'get',
               dataType: 'json',
               success : function (data) {
                    $("#modal").modal("show");
                    $("#modal .modal-content").html(data.html)
               }
        });
     }
   });
});
