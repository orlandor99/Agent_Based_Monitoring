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
        stage("Terraform init"){
            steps{
                dir("terraform"){
                    sh "terraform init"
                }
            }
        }
        stage("Generate inventory file"){
            steps{
                dir("ansible"){
                    sh "./generate_inventory.sh"
                }
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
                '''
            }
        }
        stage("Deploy"){
            steps{
                dir("ansible"){
                    withCredentials([sshUserPrivateKey(credentialsId: 'ssh-key-monitor', keyFileVariable: 'SSH_KEY')]) {
                        sh "ansible-playbook -i inventory playbook.yaml --private-key \$SSH_KEY"
                    }
                }
            }
        }
    }
}
