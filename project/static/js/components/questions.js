$(document).ready(function () {
    var params = getUrlParams();
    $.each(params, function(index, value) {
        if(index == 'q'){
            $('input[name=' + index + ']').val(value);
        } else if (index == 'category'){
            var categories = value.split(",");
            for (var i=0; i < categories.length; i++){
                 $('input:checkbox[name=' + index + ']').filter('[value=' + categories[i] + ']').attr('checked', true);
            }
        }
    });

    function returnUrl(){
        var categories = $('input[name="category"]:checked').serialize();
        var search = $('input[name="q"]').serialize();
        var url = '?';
        if(search && categories){
            url += search + '&' + categories;
        } else if(search){
            url += search;
        } else{
            url += categories;
        }
        return url;
    }

    $('#search').on('keydown', function(e) {
        if (e.which == 13) {
            location.href = returnUrl();
        }
    });

    $(".category").change(function() {
        location.href = returnUrl();
    });
});