pipeline {
    agent any
    stages {
        stage("Build") {
            steps {
                script {
                    def image = docker.build("docker.io/vladpbr/overengineered-chess-client:${env.BUILD_ID}", "-f ${env.WORKSPACE}/client/Dockerfile ${env.WORKSPACE}/client")
                    image.push()
                }
            }
        }
    }
}