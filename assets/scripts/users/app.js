$('input[name="user_logo"]').on('change', function () {
   if (typeof (FileReader) != "undefined") {
      var image_holder = $("#preview");
      image_holder.empty();
      var file = this.files[0];
      var imagefile = file.type;
      var file_size = file.size;
      var match= ["image/jpeg","image/png","image/jpg","image/gif"];
      if (!((imagefile==match[0]) || (imagefile==match[1]) || (imagefile==match[2]) || (imagefile==match[3]))) {
        $("#user_logo").val('');
        $("#user_logo").replaceWith($("#user_logo").clone(true));
        $("<small />", {
                "class" : "error",
                "text" : "Allowed extensions are: jpg, jpeg, gif, png.."
            }).appendTo(image_holder);
        return false;
      }
      else if (file_size > 20*1024) { // 2MB = 2097152 kB = 1024 * 1024 * 2
        $("#user_logo").val('');
        $("<small />", {
                "class" : "error",
                "text" : "Logo exceeds the maximum allowed size of 20kb."
            }).appendTo(image_holder);
        return false;
      }
      else {
        var reader = new FileReader();
        reader.onload = function (e) {
            $("<img />", {
                "src": e.target.result,
                "class": "img-responsive"
            }).appendTo(image_holder);
         }
        image_holder.show();
        reader.readAsDataURL($(this)[0].files[0]);
      }
    } else {
      alert("This browser does not support FileReader.");
    }
});

//~ $(window).on('load', function () {
  //~ var va =$("#id_groups").children("option:selected").html();
  //~ if (va=="Enterprise") {
     //~ $("#enterprise_logo-group").show();    
     //~ $("#enterprise_colour-group").show();
  //~ }
  //~ else {
    //~ $("#enterprise_logo-group").hide();
    //~ $("#enterprise_colour-group").hide();
  //~ }
//~ });

//~ $("#id_groups").change(function(){
  //~ var va =$("#id_groups").children("option:selected").html();
  //~ if (va=="Enterprise"){
     //~ $("#enterprise_logo-group").show();
     //~ $("#enterprise_colour-group").show();
  //~ }
  //~ else {
    //~ $("#enterprise_logo-group").hide();
    //~ $("#enterprise_colour-group").hide();
  //~ }
//~ });

$(document).ready(function() {  
  $("option:First").text(" - Select - ");
  $("#usersubmitForm").submit(function(e) {
      var va =$("#id_groups").children("option:selected").html();
   
     //~ if (va!="Enterprise"){
        //~ $('#id_enterprise_logo').val(''); 
        //~ $('#id_enterprise_colour').val(''); 
     //~ }
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
		$('#user_submit').attr('disabled', true);
      }
    })
    .done(function(response) {
       $('.loading-overlay').fadeOut("slow");
       var focus_key = 'msg';
       console.log('response.success', response.success);
       if (response.success) { 
           var focus_key = 'msg';
           $('#usersubmitForm')[0].reset(); 
           $('#msg-group').append('<div class="alert alert-success text-success">'+response.msg+'</div>');
           if (focus_key) {
              $('html, body').animate({ 
                scrollTop:$('#'+focus_key+'-group').offset().top - ($(window).height() / 2)
              }, 500, function() { 
                 $('#'+focus_key+'-group').focus();
              });
          }
           setTimeout(function() {
              window.location.href = response.redirect_url;
           }, 3000);
           
       } 
       else if (response.success==false) {  
          var i = 0;
          focus_key = 'msg'; 
          if ( (response.msg) && (response.msg!=undefined) ) { 
             $('#msg-group').append('<div class="alert alert-danger text-danger error">'+response.msg+'</div>');
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
          
          if (focus_key) {
              $('html, body').animate({ 
                scrollTop:$('#'+focus_key+'-group').offset().top - ($(window).height() / 2)
              }, 500, function() { 
                 $('#'+focus_key+'-group').focus();
              });
          }
        }
    });
    event.preventDefault();

  });
});
