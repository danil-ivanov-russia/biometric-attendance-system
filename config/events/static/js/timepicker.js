  $(document).ready(function(){
    $('.timepicker').timepicker({
      twelveHour: false,
      defaultTime: '00:05',
      onSelect: function(hours, minutes){
        if (parseInt(hours) < 10) {
            hours   = "0" + hours;
        }
        if (parseInt(minutes) < 10) {
            minutes = "0" + minutes;
        }
        $("[name='timer']").val(hours+":"+minutes+":00");
      },
      onOpenStart: function(){
        $(".timepicker-close:contains('Cancel')").css("visibility", "hidden");
        $(".timepicker-close:contains('Ok')").text('Выбрать');
      }
    });
  });