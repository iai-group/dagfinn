# Create New Skill

Make sure [Java 8 JDK](https://www.oracle.com/java/technologies/javase/javase-jdk8-downloads.html) or [OpenJDK 8](https://adoptopenjdk.net/) is installed on your system.
To create a new skill navigate to the SDK folder and issue command:

```
gradlew createSkill --name=<skill-name> --folder=<path>
```

**NB!** If you installed SDK using the SDK launcher, the SDK is located in the user home directory inside `~/.furhat/launcher/sdk/<version>`.

# Build the Skill

Call `./gradlew shadowJar` from the skill folder.
You can find the compiled skill in `<project folder>/build/libs`. with the extension `.skill`.

# Run the Skill

You can either run the skill from the SDK launcher by selecting `Start Skill` or via the terminal:
```
java -jar <project folder>/build/libs/<name_of_skill_file>.skill
```

# Furhat Skills Documentation

 * [docs](https://docs.furhat.io/skills/)

