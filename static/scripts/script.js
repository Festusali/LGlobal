// We define a variable 'text_box' for storing the html code structure of message that is displayed in the chat box.
//var text_box = '<div class="card-panel right" style="width: 75%; position: relative">' +
//        '<div style="position: absolute; top: 0; left:3px; font-weight: bolder" class="title">{sender}</div>' + 
//        '{message} </div>';
        
    //'<div class="chat-sender"> <div class="chat-title">{sender}</div>' +
    //'<div id="chat-{id}" class="chat-detail">{message}</div></div>';

var msg_box = '<div class="float-right-container">' +
    '<div id="chat-{c_id}" class="chat-sender float-right">' +
    '<div class="chat-title">Me <br><i class="datetime">{date}</i> </div>' +
    '<div class="chat-detail">{message}</div> </div> </div>';
    
var rcv_box = '<div class="float-left-container"> <div class=""> <span class=""> <img class="avatar receiver-avatar" src="{avatar}" alt="{sender}">' +
    '</span> <span class=""> <div id="chat-{c_id}" class="chat-receiver float-left">' +
    '<div class="chat-title"><a href="/account/users/{username}/">{sender}</a> <br><i class="datetime">{date} </i> </div>' +
    '<div class="chat-detail">{message}</div> </div> </div> </span> </div>';


// Send takes three args: sender, receiver, message. sender & receiver are ids of users, and message is the text to be sent.
function send(sender, receiver, message) {
    var form = $(".chat-form");
    $.post(form.attr("action"), form.serialize(), function (data) {
        data = JSON.parse(data);
        $('#chat-board').append(parseSentChat(data[0])); // Render the message inside the chat-board by appending it at the end.
    });
}

function parseSentChat(newData) {
    console.log(newData);
    $("#c_id").val(newData.pk);
    c_date = new Date(newData.fields.date);
    var box = msg_box.replace('{date}', c_date.toDateString()+' '+c_date.toLocaleTimeString()).replace('{c_id}', newData.pk).replace('{message}', newData.fields.message); 
    
    return box;
}

function parseReceivedChat(newData) {
    console.log(newData)
    var c_date = newData.fields.date;
    console.log(newData.pk);
    $("#c_id").val(newData.pk);
    c_date = new Date(c_date);
    var box = rcv_box.replace('{sender}', receiver_name).replace('{sender}', receiver_name).replace('{c_id}', newData.pk).replace('{avatar}', getReceiverAvatar);
    box = box.replace('{username}', receiver_name).replace('{message}', newData.fields.message).replace('{date}', c_date.toDateString()+' '+c_date.toLocaleTimeString());
    
    return box;
}


// Receive function sends a GET request to '/chat/<receiver_name>/' to get all recent messages. 
function receive() {
    // receiver_name' is a global variable declared in the chats.html, which contains the name of the user.
    var lts = $("#c_id").val(); 
    console.log(lts);
    $.get('/chat/'+ receiver_name + '/?latest=' + lts, function (data) {
        console.log(data);
        data = JSON.parse(data);
        if (data.length !== 0)
        {
            for(var i=0;i<data.length;i++) {
                // If the message is from the current user
                console.log(data[i]);
                if (data[i].fields.sender == receiver_id) {
                    $('#chat-board').append(parseReceivedChat(data[i]));
                } else {
                    $('#chat-board').append(parseSentChat(data[i]));
                }
            }
        }
    });
}

//Scroll to end function
/* function scrolltoend() {
    $('#chat-board').stop().animate({
        scrollTop: $('#chat-board')[0].scrollHeight
    }, 800);
}
*/
