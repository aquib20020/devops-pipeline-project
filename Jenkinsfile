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
                script {
                    withCredentials([sshUserPrivateKey(credentialsId: 'ec2-ssh-key-system', keyFileVariable: 'SSH_KEY', usernameVariable: 'SSH_USER')]) {
                        powershell """
                            \$keyFile = \$env:SSH_KEY
                            
                            # Copy key to a permanent location with proper permissions
                            \$newKeyPath = "C:\\temp\\jenkins-ec2-key.pem"
                            New-Item -ItemType Directory -Force -Path "C:\\temp" | Out-Null
                            Copy-Item \$keyFile \$newKeyPath -Force
                            
                            # Remove all permissions
                            icacls \$newKeyPath /inheritance:r
                            
                            # Grant only current user read access
                            \$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
                            icacls \$newKeyPath /grant:r "\${currentUser}:(R)"
                            
                            # Deploy to EC2 using the properly permissioned key
                            ssh -o StrictHostKeyChecking=no -i \$newKeyPath ${EC2_USER}@${EC2_HOST} "docker pull ${DOCKER_IMAGE}:latest && docker stop devops-app || echo 'Container not running' && docker rm devops-app || echo 'Container not found' && docker run -d --name devops-app -p 80:5000 --restart unless-stopped ${DOCKER_IMAGE}:latest && docker ps"
                        """
                    }
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
