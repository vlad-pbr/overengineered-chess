backend_microservices = ['move_validator', 'endgame_validator', 'gateway']

def get_image_name(service) {
    return "vladpbr/overengineered-chess-${service}:${env.BUILD_ID}"
}

pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                script {
                    docker.withRegistry('', 'dockerio-credentials') {
                        // build client
                        def image = docker.build(get_image_name('client'), "-f ${env.WORKSPACE}/client/Dockerfile ${env.WORKSPACE}/client")

                        // build backend microservices
                        backend_microservices.each { microservice ->
                            script {
                                sh "cd ${microservice} && tar -czh . | docker build - -t ${get_image_name(microservice)}"
                            }
                        }
                    }
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    // test all backend microservices
                    backend_microservices.each { microservice ->
                        docker.image('redis:7.0.5').withRun() { c ->
                            docker.image(get_image_name(microservice)).inside("--entrypoint='' -e REDIS_HOST=${c.networksettings.ipaddress}") {
                                sh 'cd /app && pytest'
                            }
                        }
                    }
                }
            }
        }
    }
}
