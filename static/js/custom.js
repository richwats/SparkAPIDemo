// Global Variables
var debug = true
var showLoader = true

// Ajax Post CSRF
var csrftoken = $('meta[name=csrf-token]').attr('content')
$.ajaxSetup({
    dataType: 'json',
    error: function(){ location.reload() },  // Reload page on error to pickup flashes
    beforeSend: function(xhr, settings) {
        if (debug) console.log('CSRF:'+csrftoken)
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
        }
    }
})

// Ajax Loading Indicator
$(document).resize(setLoaderPosition());
$('#ajaxLoadingModal').modal('hide');

function setLoaderPosition() {
    var loaderHeight = (window.innerHeight / 2) - 102;
    var loaderWidth = (window.innerWidth / 2) - 97;
    $('#ajaxLoadingModal').css('position', 'absolute!important').css('top', loaderHeight+'px');
    
    if (debug) {
		console.log('[setLoaderPosition] Window Size: '+window.innerWidth+'px width, '+window.innerHeight+'px height');
        console.log('[setLoaderPosition] Loader Indicator Position: '+loaderWidth+'px , '+loaderHeight+'px');
    }
    
}

$(document).ajaxSend(function(event, request, settings) {
    if (debug) { console.log('[ajaxSend] Show Loading Indicator'); }
    if (showLoader){
		setLoaderPosition();
        $('#ajaxLoadingModal').modal('show')
    }
});

$(document).ajaxComplete(function(event, request, settings) {
    if (debug) { console.log('[ajaxComplete] Hide Loading Indicator'); }
    if (showLoader){
        $('#ajaxLoadingModal').modal('hide')
    }
});


// Dynamic Modal Height

$('.modal').on('show.bs.modal', function () {
    $('.modal .modal-body').css('overflow-y', 'auto'); 
    $('.modal .modal-body').css('max-height', $(window).height() * 0.65);
});


// Ajax Forms
$('.ajaxForm').ajaxForm({
    dataType:  'json',
    //beforeSerialize: orderMultiSelect,
    //success:  processResponse
    });

//function processResponse(jsonObj) {
//    if (debug) console.log('[processResponse] Ajax Response:');
//	if (debug) console.log(jsonObj)
//	
//	var successFn = eval(jsonObj.results.successFn)
//	var successParam = eval(jsonObj.results.successParam)
//	successFn(successParam)
//}


function reloadWindow(jsonObj, status){
    if (debug) {
        console.log('[custom.reloadWindow] Ajax Response Status:'+status)
        console.log(jsonObj)
    }
    location.reload()
}

// Clear Session
function clearSession() {
    //AJAX call to populate
    var data = {
      'call': 'clearSession',
    }
    // Call Initial Ajax Function
    $.post('/ajax', data, reloadWindow )
}