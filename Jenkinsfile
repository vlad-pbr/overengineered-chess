microservices = ['move_validator', 'endgame_validator', 'gateway']

pipeline {
    agent any
    stages {
        stage("Build") {
            steps {
                script {

                    // build client
                    def image = docker.build("docker.io/vladpbr/overengineered-chess-client:${env.BUILD_ID}", "-f ${env.WORKSPACE}/client/Dockerfile ${env.WORKSPACE}/client")
                    // image.push()
                
                    // build microservices
                    microservices.each { microservice ->
                        script {
                            sh "cd ${microservice} && tar -czh . | docker build - -t docker.io/vladpbr/overengineered-chess-${microservice}:${env.BUILD_ID}"
                        }
                    }
                }
            }
        }
    }
}