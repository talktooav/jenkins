$(document).ready(function() {
  $("#groupsubmitForm").submit(function(e) {
    $('.form-group').removeClass('has-error'); 
    $('.error').remove(); 
    $('#msg-group').html('');
	var form_data = new FormData(this);

    // Read selected files
    //~ var totalfiles = document.getElementById('id_upldFile').files.length;
    
    //~ for (var index = 0; index < totalfiles; index++) {
      //~ form_data.append("upldFile[]", document.getElementById('id_upldFile').files[index]);
    //~ }
    e.preventDefault();
    $.ajax({
        
            xhr: function() { 
                
                if (upload()) {
                var xhr = new window.XMLHttpRequest();
                xhr.upload.addEventListener("progress", function(evt) {
                    if (evt.lengthComputable) {
                        var percentComplete = Math.round(((evt.loaded / evt.total) * 100));
                        
                        $(".progress-bar").width(percentComplete + '%');
                        $(".progress-bar").html(percentComplete+'%');
                    }
                }, false); 
                return xhr;
            }},
            type: 'POST',
             url: $(this).attr('action'),
            data: form_data, // our data object
         enctype: 'multipart/form-data',
           async: false,
     contentType: false,
           cache: false,
     processData: false,
        dataType: 'json', 
      beforeSend: function( xhr ) {
		//~ $(".loading-overlay").show();
        //~ $(".progress-bar").width('0%');
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
              //~ if (key == 'upldFile') {
                 //~ $(".progress-bar").width('0%');
                 //~ $('.progress').hide();
              //~ }
              
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
   
   
//~ var values=$("#tagUserData").val();
//~ $.each(values.split(","), function(i,e){
    //~ $("#id_taggedusers option[value='" + e + "']").prop("selected", true);
//~ });

// $("#id_taggedusers option[value='11']").prop("selected", true);

$("#id_upldFile").change(function() {
    // check file size
    upload();
    $('#image_preview').html('');
    var total_file=document.getElementById("id_upldFile").files.length;
    for (var i=0; i < total_file; i++) {
        var file = $('#id_upldFile')[0].files[i];
        var file_type = file.type;
        if (file_type.indexOf('image/') != -1) {
           $('#image_preview').append("<img class='img-responsive' src='"+URL.createObjectURL(event.target.files[i])+"' width='200px;' height='200px'>");
        }
        else {
            comma = '';
            if (i > 0)
               comma = ', '; 
            $('#image_preview').append(comma+file.name);    
        }
    }
    $(".progress-bar").width('0%');
    $(".progress-bar").html('0%');
    $('.progress').show();
});
  
function upload() {
 
    //The maximum size that the uploaded file can be.
    var maxSizeMb = 200;
    var file = $('#id_upldFile')[0].files[0];
    //Get the file that has been selected by
    //using JQuery's selector.
    if (file !== undefined) {
        var total_file = document.getElementById("id_upldFile").files.length;
        total_size = 0;
        var file_type_err = false;
        for (var i=0; i < total_file; i++) {
            var file = $('#id_upldFile')[0].files[i];
            total_size += file.size;
            var file_type = file.type;
            ext = file_type.substr(file_type.indexOf("/") + 1);
            if ($.inArray(ext, ['jpeg', 'png', 'jpg', 'gif', 'mp4', 'pdf', 'docx', 'xlsx', 'csv', 'text', 'txt', 'xls', 'doc', 'odt', 'pptx', 'zip', 'rar', 'xlsm', 'xlsb', 'xlt', 'xml', 'mp3', 'mp4']) == -1) {
                file_type_err = true;
            }
        }
        var totalFileSizeMb = total_size  / Math.pow(1024,2);
        if (file_type_err) {
           $('#upldFile-group').addClass('has-error'); // add the error class to show red input
           $('#upldFile-group').append('<small class="error">File is not valid, please try again.</small>'); 
           return false; 
        }
        else if (totalFileSizeMb > maxSizeMb) {
           var errorMsg = 'File too large. Maximum file size is ' + maxSizeMb + 'MB. Selected file is ' + totalFileSizeMb.toFixed(2) + 'MB';
                
           //Show the error.
           $('#upldFile-group').addClass('has-error'); // add the error class to show red input
           $('#upldFile-group').append('<small class="error">'+errorMsg+'</small>'); 
           return false;
        }
        else {
           return true; 
        }
    }
    else {
       return true; 
    }
    /*
    var file = $('#id_upldFile')[0].files[0];

    //Make sure that a file has been selected before
    //attempting to get its size.
    if(file !== undefined) {

        //Get the size of the input file.
        var totalSize = file.size;
        alert(totalSize);
        //Convert bytes into MB.
        var totalSizeMb = totalSize  / Math.pow(1024,2);

        //Check to see if it is too large.
        if(totalSizeMb > maxSizeMb){
            $(".progress-bar").width('0%');
            $(".progress-bar").html('0%');
            //Create an error message to show to the user.
            var errorMsg = 'File too large. Maximum file size is ' + maxSizeMb + 'MB. Selected file is ' + totalSizeMb.toFixed(2) + 'MB';
            
            //Show the error.
            $('#upldFile-group').addClass('has-error'); // add the error class to show red input
            $('#upldFile-group').append('<small class="error">'+errorMsg+'</small>');
            
            
            //Return FALSE.
            return false;
        }
        else {
            return true;
        }

    }
    else {
        return true;
    }
    */
}
   
});
