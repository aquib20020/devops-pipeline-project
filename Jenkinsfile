pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'aquiib/devops-pipeline-app'
        EC2_HOST = '13.61.7.50'
        EC2_USER = 'ubuntu'
    }
    
    triggers {
        // Poll GitHub every 1 minute for changes
        pollSCM('* * * * *')
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo "Pulling latest code from GitHub..."
                git branch: 'main', 
                    url: 'https://github.com/aquib20020/devops-pipeline-project.git'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo "Building Docker image..."
                script {
                    docker.build("${DOCKER_IMAGE}:latest")
                }
            }
        }
        
        stage('Test Image') {
            steps {
                echo "Testing Docker image..."
                script {
                    bat "docker images | findstr ${DOCKER_IMAGE}"
                }
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                echo "Pushing image to Docker Hub..."
                script {
                    docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-credentials') {
                        docker.image("${DOCKER_IMAGE}:latest").push()
                    }
                }
            }
        }
        
        stage('Deploy to EC2') {
            steps {
                echo "Deploying to AWS EC2..."
                sshagent(credentials: ['ec2-ssh-key']) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} '
                            echo "Pulling latest Docker image..."
                            docker pull ${DOCKER_IMAGE}:latest
                            
                            echo "Stopping old container..."
                            docker stop devops-app || true
                            docker rm devops-app || true
                            
                            echo "Starting new container..."
                            docker run -d --name devops-app -p 80:5000 --restart unless-stopped ${DOCKER_IMAGE}:latest
                            
                            echo "Deployment complete!"
                            docker ps | grep devops-app
                        '
                    """
                }
            }
        }
    }
    
    post {
        success {
            echo "Pipeline completed successfully!"
            echo "Application available at: http://${EC2_HOST}/"
        }
        failure {
            echo "Pipeline failed! Check logs for details."
        }
    }
}
