pipeline{
    agent any
    environment{
        GIT_REPO = "https://github.com/orlandor99/Agent_Based_Monitoring"
        BRANCH = "main"
        DOCKER_CREDS = credentials('dockerhub-credentials')
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
                    def dockerImage = docker.build("orlandor99/monitoring-server:latest", "-f docker/Dockerfile .")
                }
            }
        }
        stage("Docker Push"){
            steps{
                sh '''
                echo $DOCKER_CREDS_PSW | docker login -u $DOCKER_CREDS_USR --password-stdin
                docker push orlandor99/monitoring-server:latest
            }
        }
    }
}
