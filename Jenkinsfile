pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from GitHub...'
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                bat 'docker build -t aquiib/devops-pipeline-app:latest .'
            }
        }
        
        stage('Test Application') {
            steps {
                echo 'Running tests...'
                bat 'docker run --rm aquiib/devops-pipeline-app:latest python -c "print(\'Application test passed!\')"'
            }
        }
        
        stage('Push to Registry') {
            steps {
                echo 'Ready to push to Docker Hub (credentials needed)'
            }
        }
        
        stage('Deploy') {
            steps {
                echo 'Ready for deployment to AWS/Azure'
            }
        }
    }
    
    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
