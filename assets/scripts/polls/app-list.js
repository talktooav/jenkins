$(window).on( 'load', searchFilter());

function searchFilter(page_num) {
    page_num     = page_num ? page_num : 1;
    var keywords = $('#keywords').val();
    $.ajax({
        type: 'GET',
        url: $('#SearchForm').attr('action'),
        data:'page='+page_num+'&keywords='+keywords,
        beforeSend: function () {
            $('.loading-overlay').show();
        },
        success: function (response) { 
           
            $('#list_view tbody tr').remove(); 
            $('.totals').html(response.total_records);
            $('#list_view').find('tbody').append(response.html);
            $('#pagination_view').html(response.pagination);
            
            //~ $('#list_view').html(response.html);
            $('.loading-overlay').fadeOut("slow");
        }
    });
}

var d = new Date();
var current_dt = d.getFullYear()+'-'+(d.getMonth()+1)+'-'+d.getDate()+'-'+d.getHours()+d.getMinutes();
$('#download-csv').on('click', function() {
    var keywords = $('#keywords').val();
    var file_name = $('#csv_file_name').val();
    //~ var imei     = $('#imei').val();
    //~ var group    = $('#group_group').val();
    //~ var date     = $('#date').val();
    
    $.get($(this).attr('data-url'), {'keywords' : keywords}, function(data) {
        var blob  = new Blob([data]);
        var link  = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = current_dt+"-"+file_name+'.csv';
        link.click();
    });
    
});
