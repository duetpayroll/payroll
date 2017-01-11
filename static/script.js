$(function() {
    $( ".date-picker" ).datepicker({
            autoclose: true,
            format: 'yyyy-mm-dd',
            showTodayButton: true
        })
    $( ".dateinput" ).datepicker({
            autoclose: true,
            format: 'yyyy-mm-dd',
            showTodayButton: true
        })
    $( "input[name='date']" ).datepicker({
        autoclose: true,
        format: 'yyyy-mm-dd',
        showTodayButton: true
    })

     $(".month-picker").datepicker({
   		autoclose: true,
            format: 'yyyy-mm-dd',
            viewMode: 'months',
            minViewMode: 'months'
		});


    $('[data-toggle="tooltip"]').tooltip();

    $(".alert.auto-fade").fadeTo(2000, 500).slideUp(500, function(){
        $(".alert.auto-fade").slideUp(500);
    });

    $("li.active").each(function () {
        parent_attr = $(this).attr('parent_id')
        $("li#" + parent_attr).addClass('active')

    })
    //$(".datepicker").after('<span class="input-group-addon"><span class="glyphicon glyphicon-calendar"></span></span>')
  });