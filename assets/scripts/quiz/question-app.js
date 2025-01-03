$(document).ready(function() {
  $("#submitForm").submit(function(e) {
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
           $('#submitForm')[0].reset(); 
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
  
  $(window).on('load', function() {
    var opt = $('.option-status:checked').val();
    change_status(opt);
  }); 
  
  function change_status(opt) {
    if (opt == 'True') {
      
      $('#optionA-group').hide();
      $('#optionAFile-group').show();
      $('#id_optionAFile').val('');
      $('#optionB-group').hide();
      $('#optionBFile-group').show();
      $('#id_optionBFile').val('');
      $('#optionC-group').hide();
      $('#optionCFile-group').show();
      $('#id_optionCFile').val('');
      $('#optionD-group').hide();
      $('#optionDFile-group').show();
      $('#id_optionDFile').val('');
    }
    else {
      
      $('#optionAFile-group').hide(); 
      $('#optionA-group').show(); 
      $('#id_optionAFile').val('');
      $('#optionBFile-group').hide(); 
      $('#optionB-group').show(); 
      $('#id_optionBFile').val('');
      $('#optionCFile-group').hide(); 
      $('#optionC-group').show(); 
      $('#id_optionCFile').val('');
      $('#optionDFile-group').hide(); 
      $('#optionD-group').show(); 
      $('#id_optionDFile').val('');
    }    
  }
  
  $('.option-status').on('change', function() {
      var opt = $(this).val();
      change_status(opt);
  });
   
});