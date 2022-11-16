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
                        image.push()

                        // build backend microservices
                        backend_microservices.each { microservice ->
                            script {
                                sh "cd ${microservice} && tar -czh . | docker build - -t ${get_image_name(microservice)}"
                                sh "docker push ${get_image_name(microservice)}"
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
                            def redis_ip = sh(script: "docker inspect -f '{{ .NetworkSettings.IPAddress }}' ${c.id}", returnStdout: true)
                            docker.image(get_image_name(microservice)).inside("--entrypoint='' -e REDIS_HOST=${redis_ip}") {
                                sh 'cd /app && pytest'
                            }
                        }
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                script {

                    // create client env config
                    sh 'docker config rm env || true'
                    sh 'docker config create env - < deploy/env.json'

                    // deploy stack
                    sh 'docker stack rm overengineered-chess || true'
                    sh "IMAGE_TAG=${env.BUILD_ID} docker stack deploy --compose-file deploy/docker-compose.yml overengineered-chess"
                }
            }
        }
    }
}
