// CHANGE IP AND PORT HERE:
const IP = "localhost"
const PORT = "5005"
//------------------------
var socket = io(`http://${IP}:${PORT}`, { path: "/furhat" });

var form = document.getElementById('form');
var input = document.getElementById('input');
var images = document.getElementById('images');
var chatwindow = document.getElementsByClassName("chatwindow"[0]);
images.style = "list-style-type: none";
var chatlist = document.getElementById('messages');


form.addEventListener('submit', function (e) {
  e.preventDefault();
  if (input.value) {
    var messageContent = input.value;
    socket.emit('user_uttered', { "message": messageContent });
    input.value = '';
  }
});
socket.on('reset_frontend', function (args) {
  location.reload()

})
socket.on('user_uttered', function (args) {
  var messageContent = args.text
  if (messageContent) {
    addMessageToChatwindow(messageContent, "usermessage")
  }
})


socket.on('bot_uttered', function (args) {
  console.log(args)
  if (isText(args)) {
    try {
      handleText(args); //Will not fail because it is checked already.
    } catch (err) {
      console.log("An error has occured: " + err);
    }
  }
  if (isImage(args)) {
    try {
      clearAllImages();
      handleImage(args.attachment.payload.src, images);
    } catch (err) {
      console.log("An error has occured: " + err);
    }
  }
  if (isIFrame(args)) {
    try {
      clearAllImages();
      handleIFrame(args.attachment.payload.src, images);
    } catch (err) {
      console.log("An error has occured: " + err);
    }
  }

  if (isCarousel(args)) {
    try {
      clearAllImages();
      handleCarousels(args);
    } catch (err) {
      console.log("An error has occured: " + err);
    }
  }
});

//Autoscroll runs every half-second
autoScrollLoop();

function addMessageToChatwindow(messageContent, messageID) {
  clearOldMessages();
  addMessageToMessages(messageContent, messageID);
  autoScroll();
}

function addMessageToMessages(messageContent, messageID) {
  var messageContainer = document.createElement("div");
  var messageBubble = document.createElement("div");
  var messageText = document.createElement("li");
  messageContainer.id = "messageContainer";
  messageBubble.id = messageID
  messageText.id = "messageText";
  messageText.textContent = messageContent;
  messageBubble.appendChild(messageText);
  messageContainer.appendChild(messageBubble);
  chatlist.appendChild(messageContainer);
}

function clearOldMessages() {
  const maxMessages = 12;
  var chatMessages = chatlist.childNodes;
  if (chatMessages.length > maxMessages) {
    chatlist.removeChild(chatMessages[0]);
  }
}

function clearAllImages() {
  while (images.firstChild) {
    images.removeChild(images.firstChild)
  }
}

function autoScroll() {
  chatlist.scrollTop = chatlist.scrollHeight;
  images.scrollTop = images.scrollHeight;
}

function autoScrollLoop() {
  autoScroll();
  setTimeout(autoScrollLoop, 500);
}

function handleImage(args, docLocation, imgid) {
  var img = document.createElement('img');
  img.src = args;
  img.id = imgid;
  img.style = "width: 100%";

  if (docLocation.id == "card") {
    docLocation.appendChild(img);
    images.appendChild(docLocation);
  }

  var item = document.createElement('li');
  item.appendChild(img);
  images.appendChild(item);

}

function handleIFrame(args, docLocation, imgid) {
  var iframe = document.createElement('iframe');
  iframe.src = args;
  iframe.id = imgid;
  iframe.height = 600;
  iframe.width = 400;

  if (docLocation.id == "card") {
    docLocation.appendChild(iframe);
    images.appendChild(docLocation);
  }

  var item = document.createElement('li');
  item.appendChild(iframe);
  images.appendChild(item);

}

function handleText(args) {
  //console.log("this is args handletext",args)
  var messageContent = args.text;
  addMessageToChatwindow(messageContent, 'botmessage')
}

function handleCarousels(args) {
  var elements = args.attachment.payload.elements;
  console.log(elements);
  for (let i = 0; i < elements.length; i++) {

    var card_info = elements[i];
    var card = document.createElement("div");
    card.id = "card";
    var title = document.createElement("div");
    title.textContent = card_info['title'];
    title.id = "title";
    card.appendChild(title);

    if (args.attachment.payload.elements[i].subtitle) {
      var subtitle = document.createElement("div");
      subtitle.textContent = card_info['subtitle'];
      subtitle.id = "subtitle";
      card.appendChild(subtitle);
    }
    if (card_info['image_url']) {
      try {
        handleImage(card_info['image_url'], card, "image_url");
      } catch (err) {
        console.log("An error has occured: " + err);
      }
    }
    if (card_info['iframe_url']) {
      try {
        handleIFrame(card_info['iframe_url'], card, "iframe_url");
      } catch (err) {
        console.log("An error has occured: " + err);
      }
    }
  }
}

// check if is text message
function isText(message) {
  return Object.keys(message).includes('text');
}

//check if is image
function isImage(message) {
  return Object.keys(message).includes('attachment')
    && Object.keys(message.attachment).includes('type')
    && message.attachment.type === 'image';
}

//check if is iFrame
function isIFrame(message) {
  return Object.keys(message).includes('attachment')
    && Object.keys(message.attachment).includes('type')
    && message.attachment.type === 'iframe';
}

//check if is button
function isButton(message) {
  return Object.keys(message).length === 2
    && Object.keys(message).includes('text')
    && (Object.keys(message).includes('quick_replies') ||
      Object.keys(message).includes('buttons'));
}

//check if is carousel
function isCarousel(message) {
  return Object.keys(message).includes('attachment')
    && Object.keys(message.attachment).includes('type')
    && message.attachment.type === 'template'
    && Object.keys(message.attachment).includes('payload')
    && Object.keys(message.attachment.payload).indexOf('template_type') >= 0
    && message.attachment.payload.template_type === 'generic'
    && Object.keys(message.attachment.payload).indexOf('elements') >= 0
    && message.attachment.payload.elements.length > 0;
}



