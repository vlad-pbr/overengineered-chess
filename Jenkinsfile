pipeline {
    agent any
    stages {
        stage("Build") {
            steps {
                echo "Nice build"
                script {
                    def image = docker.build("my-image:latest", "-f ${env.WORKSPACE}/gateway/Dockerfile .")
                }
            }
        }
    }
}