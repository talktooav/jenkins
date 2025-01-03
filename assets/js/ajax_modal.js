var d = new Date($.now());
var current_dt = d.getDate()+"-"+(d.getMonth() + 1)+"-"+d.getFullYear()+"-"+d.getHours()+"-"+d.getMinutes()+"-"+d.getSeconds();

$('#SearchForm').on('keyup keypress', function(e) {
  var keyCode = e.keyCode || e.which;
  if (keyCode === 13) { 
    e.preventDefault();
    return false;
  }
});

$(document).ready(function() {
  // unchecked checkbox on cancel button
  $('body').on('click', '.close, .cancel', function() {
      var un = $('.content').find('input.list_item:checked').attr('checked', false);
  });
  
  $('#checkall-toggle').click(function(event) {  
    if ($(this).is(":checked")) {
       $("#allDel").show()
    }
    else {
      $("#allDel").hide()
    }
    if (this.checked) {
       // Iterate each checkbox
       $(':checkbox').each(function() {
            this.checked = true;
       });
    }
    else {
      $(':checkbox').each(function() {
        this.checked = false;                       
      });
    }
  });

$("#allDel").hide()
$('.content').on('click', '.delBtn', function() {
    
    $('#modal').modal({ backdrop: 'static', keyboard: false }); 
    var unchecked =  $('input.list_item:checked').attr('checked', false);
    var mapped = $(this).closest('tr').children('th:first').find('input:checkbox').prop('checked', true);
    
    var seln_count = $('input.list_item:checked').length;
    if (seln_count==0)
        alert('select records to delete!');
    else { 
      $.ajax({
        url:$(this).attr('data-url'),
        type: 'get',
        dataType: 'json',
        success : function (data) {
            $("#modal").modal("show");
           $("#modal .modal-content").html(data.html)
          
        }
      });
      
    }
    
});

$('.content').on('click', '.delbtn', function() {
    
    $('#modal').modal({ backdrop: 'static', keyboard: false }); 
    var unchecked =  $('input.list_item:checked').attr('checked', false);
    var mapped = $(this).closest('tr').children('th:first').find('input:checkbox').prop('checked', true);
    
    var seln_count = $('input.list_item:checked').length;
    if (seln_count==0)
        alert('select records to delete!');
    else { 
      $.ajax({
        url:$(this).attr('data-url'),
        type: 'get',
        dataType: 'json',
        success : function (data) {
            $("#modal").modal("show");
           $("#modal .modal-content").html(data.html)
          
        }
      });
      
    }
    
});

$('.content').on('click', '.allDel', function() {

    var mapped = $(this).closest('tr').children('th:first').find('input:checkbox')
    
    var seln_count = $('input.list_item:checked').length;
    if (seln_count==0)
        alert('select records to delete!');
    else { 
      $.ajax({
         url:$(this).attr('data-url'),
         type: 'get',
         dataType: 'json',
         success : function (data) {
            $("#modal").modal("show");

           $("#modal .modal-content").html(data.html)
          
         }
      });
      
    }
    
});
  
var DeleteFormlist = function() {
    var form = $(this);
    $(this).find('.btn-danger').attr('disabled', true);
    var seln_count = $('input.list_item:checked').length;
    if (seln_count==0)
       alert('select records to delete!');
    else {
      var btn = $(this);
      var ids = [];
      
      $("input.list_item:checked").each(function() { 
          ids.push($(this).val()); 
      });
    $.ajax({
       url: form.attr("action"),
       data: {'ids':ids},
       type: 'POST',
       dataType: 'json',
       success: function (response) {
         if (response.success) {
            $('#del-msg-group').html('<div class="alert alert-success text-success">'+response.msg+'</div>');
            setTimeout(function() {
              $("#modal").modal("hide");
              window.location.href = '';
              //~ searchFilter();
            }, 3000);
            
         }
         else {
           $('#del-msg-group').html('<div class="alert alert-danger text-danger error">'+response.msg+'</div>');
           setTimeout(function() {
              $("#modal").modal("hide");
              window.location.href = '';
              //~ searchFilter();
           }, 3000);
         }
       }
    });
    return false;
  }
}

$("body").on('submit', '#confirmDelete', DeleteFormlist);  
});

// hide all delete button on unchecked and show on checked
$('.devices-sec').on('click', '.list_item', function() {
  if (this.checked) {
     $("#allDel").show()
  }
  else{
      var checked = false
      $(':checkbox').each(function() {
         if (this.checked==true) {
            checked = true;
         }
      });
      if (checked==true)
         $("#allDel").show()
      else
         $("#allDel").hide()
  }
});
// hide all delete button on unchecked and show on checked


//clear filter
$('.cross-icon').on('click', function() {
   $("input[type=text], text").val("");
   $("option:selected").prop("selected", false);
   searchFilter();
});

$('.refresh-icon').on('click', function() {
    window.location.href='';    
});

$("input").keypress(function() { 
  $(this).closest('.form-group').removeClass('has-error'); 
  $(this).parent().find('.error').remove(); 
  $('#msg').html('');
  $('#msg-group').html('');
  $('input[type=submit]').attr('disabled', false);
}); 
  
$( "select" ).change(function() { 
  $(this).closest('.form-group').removeClass('has-error'); 
  $(this).closest('.form-group').find('.error').remove(); 
  $('input[type=submit]').attr('disabled', false);
}); 


function copyCmd(containerid) {
  if (document.selection) {
    var range = document.body.createTextRange();
    range.moveToElementText(document.getElementById(containerid));
    range.select().createTextRange();
    document.execCommand("copy");
  } 
  else if (window.getSelection) {
    var range = document.createRange();
    range.selectNode(document.getElementById(containerid));
    window.getSelection().addRange(range);
    document.execCommand("copy");
  }
}
  
$("input").click(function() { 
  var keyy = $(this).attr('name');
  if (keyy != undefined)
    keyy = keyy.replace('[]', ''); 
  $(this).closest('.form-group').removeClass('has-error'); 
  $('#'+keyy+'-group').find('.error').remove(); 
  $('#msg-group').html('');
  $('input[type=submit]').attr('disabled', false);
});
 
$("textarea").click(function() { 
  var keyy = $(this).attr('name');
  keyy = keyy.replace('[]', ''); 
  $(this).closest('.form-group').removeClass('has-error'); 
  $('#'+keyy+'-group').find('.error').remove(); 
  $('#msg-group').html('');
  $('input[type=submit]').attr('disabled', false);
}); 
