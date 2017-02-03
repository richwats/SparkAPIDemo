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


function buildMessage(msgObj,idx) {
    //Build HTML for Message

    /*
     <div class="row msg_container base_sent">
        <div class="col-md-10 col-xs-10">
            <div class="messages msg_sent">
                <p>that mongodb thing looks good, huh?
                tiny master db, and huge document store</p>
                <time datetime="2009-11-13T20:00">Timothy 51 min</time>
            </div>
        </div>
        <div class="col-md-2 col-xs-2 avatar">
            <img src="http://www.bitrebels.com/wp-content/uploads/2011/02/Original-Facebook-Geek-Profile-Avatar-1.jpg" class=" img-responsive ">
        </div>
    </div>
    */
    
    var $rowDiv = $('<div>').addClass('row msg_container').data('idx',idx)
    var $msgColDiv = $('<div>').addClass('col-md-10 col-xs-10')
    var $msgDiv = $('<div>').addClass('messages').appendTo($msgColDiv)
    
    // DisplayName
    var $fromP = $('<p>').addClass('msg_displayName').text(msgObj.displayName).appendTo($msgDiv)
    
    // Message
    if (msgObj.html != null) {
        msgData = msgObj.html
    }
    else if (msgObj.markdown != null) {
        msgData = msgObj.markdown
    }
    else {
        msgData = msgObj.text
    }
    var $msgP = $('<p>').html(msgData).appendTo($msgDiv)
    
    // Time
    var date = new Date(msgObj.created)
    var $time = $('<time>').attr('datetime', msgObj.created).text(date.toLocaleString({'timeZoneName':'long'})).appendTo($msgDiv)
    
    var $avaColDiv = $('<div>').addClass("col-md-2 col-xs-2 avatar")
    // Get Personal Avatar
    
    if (msgObj.avatar != null) {
        imgSrc = msgObj.avatar
    }
    else {
        imgSrc = 'http://www.bitrebels.com/wp-content/uploads/2011/02/Original-Facebook-Geek-Profile-Avatar-1.jpg'
    }
    
    if (debug) console.log('[buildMessage] Avatar Link:'+msgObj.avatar)
    
    var $avaImg = $('<img>').attr('src',imgSrc).addClass('img-responsive').appendTo($avaColDiv)
    
    // Apply Directional Classes
    if (msgObj.direction == "sent") {
        $rowDiv.addClass('base_sent')
        $msgDiv.addClass('msg_sent')
        $msgColDiv.appendTo($rowDiv)
        $avaColDiv.appendTo($rowDiv)
    }
    else {
        $rowDiv.addClass('base_receive')
        $msgDiv.addClass('msg_receive')
        $avaColDiv.appendTo($rowDiv)
        $msgColDiv.appendTo($rowDiv)
    }
    
    // Return JQuery Object
    return $rowDiv

}


function displayMessages(msg) {
    if (msg == null) {
        return
    }
    if (debug) console.log('[socket.io] Displaying Messages')
    //$('#messages').empty()
    for (idx in messages){
        //console.log('[socket.io] Checking Idx:'+idx)
        var match = false
        //$('li').each(function(){
        $('.msg_container').each(function(){
            if ($(this).data('idx') == idx ) {
                match = true
            }
        })
        if (match == true) {
            idx++
            continue
        }

        //Adding New Entry
        if (debug) console.log('[socket.io] Adding New Message Idx:'+idx)
        
        //var $msg = $('<li>').attr('data-idx',idx).text(messages[idx].text)
        var msgObj = messages[idx]
        var $msg = buildMessage(msgObj,idx)
        $('#messages').append($msg)
    
    }
}

function sendMessage() {
    msg = $('#msgText').val()
    if (debug) console.log('[socket.io] Sending Message: '+msg)
    // Emit Message
    socket.emit('message', msg);
    messages.push({'direction':'sent','text':msg})
    // Reset Input
    $('#msgText').val('')
    // Display Message
    displayMessages(true)
}

function openChatWS() {
    //code
    socket = io('/sparkchat');
    
    socket.on('message', function(msg){
        if (debug) console.log('[socket.io] Received Message:')
        if (debug) console.log(msg)
        //$('#messages').append($('<li>').text(msg));
        messages.push(
                        {
                        'direction':'received',
                        'displayName': msg.displayName,
                        'text':msg.text,
                        'markdown': msg.markdown,
                        'html': msg.html,
                        'created': msg.created,
                        'avatar':msg.avatar
                        }
                      )
        if (debug) console.log(messages)
        displayMessages(msg)
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
