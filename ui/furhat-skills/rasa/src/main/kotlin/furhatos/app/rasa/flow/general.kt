package furhatos.app.rasa.flow

import furhatos.flow.kotlin.*
import furhatos.util.*
import furhatos.*

val Idle: State = state {
    init {
        val names_list = listOf(
        "What is the longest fjord in Norway", "Could you please read my QR code?",
        "Can you tell me a joke", "What time is it", "What is the weather", "What is the capital",
        "Which mountain is the highest in the world?", "Which fjord is the longest fjord of Norway?",
        "Which mountain is the highest in Norway", "What time is it now?", "Will it rain today?",
        "What is interesting to see in Stavanger area?", "is highest in norway", "the longest fjord in Norway",
        "Do you have a girlfriend", "Northern Lights", "Aurora Borealis", "Nice name", "Do you like Siri", "Do you like to sing",
        "Do you like singing", "DAGFiNN", "What is the weather", "Can you recognize me", "by bus", "by taxi", "burgers, but without meat", "recommend me a session", "that's a nice name", "do you remember me"
        )
        furhat.setSpeechRecPhrases(names_list)
        furhat.cameraFeed.enable()
        furhat.setVoice(Language.ENGLISH_US, Gender.MALE)
        users.setSimpleEngagementPolicy(2.0, 3)
        // Set the inner space to a circle of 2.0 meters 
        // (outer distance becomes 2.5) and maximum users to 3
        // Default is 1.0, and 2 users.
        goto(Start)
    }
    onUserEnter {
        furhat.attend(it)
        goto(Start)
    }
    onUserLeave {
        furhat.say("Don't Leave me")
    }
}

val Interaction: State = state {
    var noinput = 0
    var nomatch = 0

    onUserEnter(instant = true) {
        // let furhat attend a user, 
        // but not change focus if already attending a user
        if (users.count == 1){
            furhat.attend(it)
        }else{
            furhat.glance(it)
        }
    }

    onUserLeave(instant = true) {
        if (users.count > 0) {
            if (it == users.current) {
                furhat.attend(users.other)
                goto(Start)
            } else {
                furhat.glance(it)
            }
        } else {
            delay(1000)         
            // delay for 1000ms = 1second, to avoid flickering failure 
            // to detect a user to result in a reset
            if (users.count > 0) {
                goto(Start)
            }else{
                socketConnection.emit_reset()
                goto(Idle)
                }
            }
            
    }

    onResponse {
        nomatch++
        if (nomatch > 1)
            furhat.say("Sorry, I still didn't understand that")
        else
            furhat.say("Sorry, I didn't understand that")
        reentry()
    }

    onNoResponse {
        noinput++
        // if (noinput > 1)
        //     furhat.say("test; Sorry, I still didn't hear you")
        // else
        //     furhat.say("Sorry, I didn't hear you")
        reentry()
    }

    onResponseFailed {
        furhat.say("Sorry, my speech recognizer is not working")
        terminate()
    }

}
