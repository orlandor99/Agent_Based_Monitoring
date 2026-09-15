pipeline{
    agent any
    environment{
        GIT_REPO = "https://github.com/orlandor99/Agent_Based_Monitoring"
        BRANCH = "main"
    }
    stages{
        stage("Checkout"){
            steps{
                git branch: "${BRANCH}", url: "${GIT_REPO}"
            }
        }
        stage("Docker Build"){
            steps{
                script{
                    dockerImage = docker.build("orlandor99/monitoring-server:latest", "-f docker/Dockerfile .")
                }
            }
        }
        stage("Docker Push"){
            steps{
                script{
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-credentials')
                        dockerImage.push()
                }
            }
        }
    }
}