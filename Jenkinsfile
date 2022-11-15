pipeline {
    agent any
    stages {
        stage("Build") {
            steps {
                echo "Nice build"
                def image = docker.build("my-image:latest", "-f ${env.WORKSPACE}/gateway/Dockerfile .")
            }
        }
    }
}