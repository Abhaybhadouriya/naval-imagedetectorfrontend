pipeline {
    agent none
    environment {
        DOCKERHUB_CREDENTIALS = credentials('DockerHubCred')
        DOCKERHUB_USERNAME = 'navalbisht444'
        REPO_URL = 'https://github.com/Naval-Bisht/imagedetectorfrontend.git'
        EMAIL_RECIPIENT = 'navalbisht444@gmail.com'
        FRONTEND_IMAGE = "${DOCKERHUB_USERNAME}/image-processing-frontend"
        BACKEND_IMAGE = "${DOCKERHUB_USERNAME}/image-processing-backend"
    }
    triggers {
        githubPush()
    }
    stages {
        stage('Checkout') {
            agent any
            steps {
                script {
                    checkout([$class: 'GitSCM',
                              branches: [[name: '*/main']],
                              userRemoteConfigs: [[url: "${REPO_URL}"]]])
                }
            }
        }

        // Frontend Pipeline
        stage('Build Frontend Docker Image') {
          
            steps{
                script{
                        frontendImage = docker.build("${FRONTEND_IMAGE}", './maskdetector/')
                }
	        }
        }

        stage('Verify Frontend Docker Image') {
            agent any
            steps {
                sh """
                    docker run --rm ${FRONTEND_IMAGE}:${env.BUILD_NUMBER} nginx -t
                """
            }
        }

        stage('Push Frontend Docker Image') {
            agent any
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'DockerHubCred') {
			         frontendImage.push()
                    }
                }
            }
        }

        // Backend Pipeline
        stage('Build Backend Docker Image') {
            agent any
            steps{
                script{
                        backendImage = docker.build("${FRONTEND_IMAGE}", './maskdetectorbackend/')
                }
	        }
        }

        stage('Verify Backend Docker Image') {
            agent any
            steps {
                sh """
                    docker run --rm ${BACKEND_IMAGE}:${env.BUILD_NUMBER} python --version
                """
            }
        }

        stage('Push Backend Docker Image') {
            agent any
            
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'DockerHubCred') {
			        backendImage.push()
                    }
                }
            }
        }

        // stage('Run Model Test') {
        //     agent {
        //         docker {
        //             image 'python:3.10'
        //             args '-u root'
        //         }
        //     }
        //     steps {
        //         dir('maskdetectorbackend') {
        //             sh 'pip install --no-cache-dir -r requirements.txt'
        //             sh 'python -m unittest discover -s . -p "test_*.py" || true'
        //         }
        //     }
        // }

        stage('Deployment using Ansible'){
            steps{
                    sh 'ansible/ansible-playbook deploy.yaml'
            }
        }

        stage('Verify Deployment') {
            agent any
            steps {
                sh 'kubectl get pods -n default'
                sh 'kubectl get svc -n default'
            }
        }
    }

    post {
        always {
            node('master') {
                script {
                    sh """
                        docker rmi ${FRONTEND_IMAGE}:${env.BUILD_NUMBER} || true
                        docker rmi ${FRONTEND_IMAGE}:latest || true
                        docker rmi ${BACKEND_IMAGE}:${env.BUILD_NUMBER} || true
                        docker rmi ${BACKEND_IMAGE}:latest || true
                    """
                    cleanWs()
                }
                emailext (
                    subject: "Build ${currentBuild.fullDisplayName} - ${currentBuild.result}",
                    body: """Build status: ${currentBuild.result}
                             Check details here: ${env.BUILD_URL}""",
                    to: "${EMAIL_RECIPIENT}"
                )
            }
        }
    }
}