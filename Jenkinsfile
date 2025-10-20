pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'aquiib/devops-pipeline-app'
        EC2_HOST = '13.61.7.50'
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
        
        stage('Deployment Notification') {
            steps {
                echo "Docker image pushed to Docker Hub successfully!"
                echo "EC2 will auto-pull and deploy within 60 seconds via cron job"
                echo "Application URL: http://${EC2_HOST}/"
            }
        }
    }
    
    post {
        success {
            echo "=========================================="
            echo "Pipeline completed successfully!"
            echo "Image: ${DOCKER_IMAGE}:latest"
            echo "Registry: Docker Hub"
            echo "Deployment: Automatic (EC2 cron-based pull)"
            echo "Production: http://${EC2_HOST}/"
            echo "Deployment ETA: less than 60 seconds"
            echo "=========================================="
        }
        failure {
            echo "Pipeline failed! Check logs for details."
        }
    }
}
