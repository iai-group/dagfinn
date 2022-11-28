Running the frontend.

step1:  
> Install Node.js and make sure to include NPM. Add to path.

go folder ui\furhat-skills\rasa\assets\webchat\

run
>npm install
then
>npm run build


go folder ui\furhat-skills\rasa\

run
gradlew shadowJar

the furhat skill will be under ui\furhat-skills\rasa\build\libs
* rasa-all.skill

If you make any changes to backend, you have to recompile with gradlew shadowJar.
If you make any changes to frontend, you have to recompile with npm run build AND gradlew shadowJar