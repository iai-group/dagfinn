package furhatos.app.rasa.flow

import furhatos.flow.kotlin.State
import furhatos.flow.kotlin.furhat
import furhatos.flow.kotlin.onResponse
import furhatos.flow.kotlin.state
import furhatos.gestures.Gestures
import io.socket.client.IO
import io.socket.client.Socket
import org.json.JSONObject
import furhatos.event.Event

import java.util.*
import furhatos.event.EventSystem

import java.util.regex.Pattern

// CHANGE IP AND PORT HERE:
val IP = "localhost"
val PORT = "5005"
//-------------------------

class EmojiChecker(){
    var regex = "[^\\p{L}\\p{N}\\p{P}\\p{Z}]".toRegex();
    init{
    }
    fun replaceAll(text:String ):String{
        return regex.replace(text, "")
    }
}

/* 
A socketIO connector class that connects to the RASA socket.io-server. 
It tries to connect on initiation of the class object. 
It also has methods for handling events to and from the rasa server.
*/

class Socketioconnector() {

    var options: IO.Options = IO.Options.builder()
            .setPath("/furhat")
            .build()

    val mSocket = IO.socket("ws://$IP:$PORT", options);
    var emojichecker = EmojiChecker()
    
    init {
        mSocket.connect();
        mSocket.on(Socket.EVENT_CONNECT_ERROR) {
            println("connection error... is rasa server running?")
        }
        mSocket.on(Socket.EVENT_CONNECT) {
            println("connected with socket.id: ");  
            println(mSocket.id());
        }
        /*JSON PARSING and info extracting */
        mSocket.on("bot_uttered") { args ->
        
            if (args[0] != null) {
                var text = ""
                var emote = ""

                var eventJson = args[0] as JSONObject
                // Get text if it's there
                if (eventJson.has("text")) {
                    //removes emojis and other uncommon characters
                    text = emojichecker.replaceAll(eventJson.get("text").toString())
                }
                // get custom expression if it's there
                if (eventJson.has("expression")) {
                    var expression = eventJson.get("expression") as JSONObject
                    emote = expression.get("expression_type").toString()
                }
                // EventSystem can send events into the flow
                if (text != ""){
                    EventSystem.send(Response_event(text, emote))
                }else if (emote != ""){
                    EventSystem.send(Response_event(text, emote))   
                }
                
                }
            }
        }

    fun emitToRAsa(utterance:String){
        mSocket.emit("user_uttered",mapOf("message" to utterance))
    }
    fun emit_reset(){
        mSocket.emit("reset_story")
    }

}
    
// Custom response event
class Response_event(val utter : String, val emote : String) : Event("Response_event")
    


var socketConnection = Socketioconnector()

val Start : State = state(Interaction) {

    // map \ dict for facial expressions
    var expression_map = mapOf(
        "anger" to Gestures.ExpressAnger,
        "shakehead" to Gestures.Shake,
        "nod" to Gestures.Nod,
        "wink" to Gestures.Wink,
        "surprise" to Gestures.Surprise,
        "smile" to Gestures.Smile
        )
    onEntry {
        //furhat.gesture(Gestures.Thoughtful) 
        furhat.listen(timeout = 30000)
        
    }
    onEvent<Response_event>{
        var expression = expression_map[it.emote]
        if(expression != null){
            furhat.gesture(expression)
        }
        // check to stop furhat from trying to speak if the event doesnt contain text, such as
        // as an image or emote event
        if (it.utter != ""){
            furhat.say(it.utter)
        }
        // delay to prevent, or reduce the likelihood of furhat picking up its own voice
        delay(800)
        furhat.listen(timeout = 30000)
    }
    onResponse{
        // onResponse should only be called if Furhat picks up some voice and it.text exits.
        socketConnection.emitToRAsa(it.text)
    }
}
