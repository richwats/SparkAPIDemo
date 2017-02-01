// Basic Chat Javascript //

// WebSocket IO //

var socket
var messages = []


//function openChatWindow() {
//    
//    // HERE - Don't like var user, don't like using local cookie ... prefer server side content with loadModal - rename chatLoginModal to chatModal?
//    
//    if (document.cookie == null) {
//        // Open Login Form Modal
//        $('#chatLoginModal').modal('show')
//    }
//    else {
//        // Open Chat Window Modal
//        $('#chatWindow').modal('show')
//    }
//    //code
//}

$('#chatModal').on('show.bs.modal',function(evt){
    // Chat Window Open
    if (debug) { console.log('[chat] Loading Chat Modal'); }
    
    $('#chatModalContent').empty().load('/loadModal/chatModal/')
    
    setInterval(displayMessages, 1000)
    
    
    openChatWS()

    
    
    })

$('#chatModal').on('hide.bs.modal',function(evt){
    // Chat Window Open
    if (debug) { console.log('[chat] Hiding Chat Modal'); }
    
    //$('#chatModalContent').empty().load('/loadModal/chatModal')
    socket.disconnect();
    
    })


//$('#minim_chat_window').click(function (e) {
//    var $this = $(this);
//    if (!$this.hasClass('panel-collapsed')) {
//        $this.parents('.panel').find('.panel-body').slideUp();
//        $this.addClass('panel-collapsed');
//        $this.removeClass('glyphicon-minus').addClass('glyphicon-plus');
//    } else {
//        $this.parents('.panel').find('.panel-body').slideDown();
//        $this.removeClass('panel-collapsed');
//        $this.removeClass('glyphicon-plus').addClass('glyphicon-minus');
//    }
//});

$(document).on('focus', '.panel-footer input.chat_input', function (e) {
    var $this = $(this);
    if ($('#minim_chat_window').hasClass('panel-collapsed')) {
        $this.parents('.panel').find('.panel-body').slideDown();
        $('#minim_chat_window').removeClass('panel-collapsed');
        $('#minim_chat_window').removeClass('glyphicon-plus').addClass('glyphicon-minus');
    }
});
//
//$(document).on('click', '#new_chat', function (e) {
//    var size = $( ".chat-window:last-child" ).css("margin-left");
//     size_total = parseInt(size) + 400;
//    alert(size_total);
//    var clone = $( "#chat_window_1" ).clone().appendTo( ".container" );
//    clone.css("margin-left", size_total);
//});

//$(document).on('click', '.icon_close', function (e) {
//    //$(this).parent().parent().parent().parent().remove();
//    $( "#chat_window_1" ).remove();
//});





function displayMessages() {
    console.log('[socket.io] Displaying Messages')
    //$('#messages').empty()
    for (idx in messages){
        var match = false
        $('li').each(function(){
            if ($(this).data('idx') == idx ) {
                match = true
            }
        })
        if (match == true) {
            continue
        }

        //Adding New Entry
        console.log('[socket.io] Adding New Message')
        var $msg = $('<li>').attr('data-idx',idx).text(messages[idx].text)
        $('#messages').append($msg)
    
    }
}

function sendMessage() {
    msg = $('#msgText').val()
    console.log('[socket.io] Sending Message: '+msg)
    // Emit Message
    socket.emit('message', msg);
    messages.push({'direction':'sent','text':msg})
    // Reset Input
    $('#msgText').val('')
}

function openChatWS() {
    //code
    socket = io('/sparkchat');
    
    socket.on('message', function(msg){
        console.log('[socket.io] Message: '+msg)
        //$('#messages').append($('<li>').text(msg));
        messages.push({'direction':'received','text':msg.text})
        console.log(messages)
        displayMessages()
    });
    
    socket.on('connect', function(){
        console.log('[socket.io] Connect Event')
        });
    
    socket.on('alert', function(data){
        console.log('[socket.io] Alert: '+data.message)
        });
    
    socket.on('disconnect', function(){
        console.log('[socket.io] Disconnect Event')
        });
    
    
}
