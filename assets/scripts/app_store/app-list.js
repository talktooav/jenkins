$(window).on( 'load', searchFilter());

function searchFilter(page_num) {
    page_num     = page_num ? page_num : 1;
    var keywords = $('#keywords').val();
    var name     = $('#name').val();
    var version  = $('#version').val();
    var package  = $('#package').val();
    var type     = $('#type').val();
    $.ajax({
        type: 'GET',
        url: $('#SearchForm').attr('action'),
        data:'page='+page_num+'&keywords='+keywords+'&name='+name+'&version='+version+'&package='+package+'&type='+type,
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
