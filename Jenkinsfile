microservices = ['move_validator', 'endgame_validator', 'gateway']

def get_image_name(service) {
    return "docker.io/vladpbr/overengineered-chess-${service}:${env.BUILD_ID}"
}

pipeline {
    agent any
    stages {

        stage("Build") {
            steps {
                script {

                    docker.withRegistry('https://docker.io', 'dockerio-credentials') {

                        // build client
                        def image = docker.build(get_image_name("client"), "-f ${env.WORKSPACE}/client/Dockerfile ${env.WORKSPACE}/client")
                        image.push()
                    
                        // build microservices
                        microservices.each { microservice ->
                            script {
                                sh "cd ${microservice} && tar -czh . | docker build - -t ${get_image_name(microservice)}"
                                sh "docker push ${get_image_name(microservice)}"
                            }
                        }

                    }
                }
            }
        }



    }
}