package furhatos.app.rasa

import java.nio.file.Paths
import kotlin.text.*
import furhatos.app.rasa.flow.*
import furhatos.skills.Skill
import furhatos.flow.kotlin.*
import furhatos.nlu.LogisticMultiIntentClassifier
import furhatos.skills.HostedGUI


class RasaSkill : Skill() {
    override fun start() {
        Flow().run(Idle)
        
    }
}
fun main(args: Array<String>) {
    Skill.main(args)
}
