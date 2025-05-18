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
            agent {
                docker {
                    image 'node:18'
                    args '-u root'
                }
            }
            steps {
                dir('maskdetector') {
                    sh 'npm install'
                    sh 'npm run build'
                    sh """
                        docker build -t ${FRONTEND_IMAGE}:${env.BUILD_NUMBER} .
                        docker tag ${FRONTEND_IMAGE}:${env.BUILD_NUMBER} ${FRONTEND_IMAGE}:latest
                    """
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
                        sh """
                            docker push ${FRONTEND_IMAGE}:${env.BUILD_NUMBER}
                            docker push ${FRONTEND_IMAGE}:latest
                        """
                    }
                }
            }
        }

        // Backend Pipeline
        stage('Build Backend Docker Image') {
            agent {
                docker {
                    image 'python:3.10'
                    args '-u root'
                }
            }
            steps {
                dir('maskdetectorbackend') {
                    sh 'pip install --no-cache-dir -r requirements.txt'
                    sh """
                        docker build -t ${BACKEND_IMAGE}:${env.BUILD_NUMBER} .
                        docker tag ${BACKEND_IMAGE}:${env.BUILD_NUMBER} ${BACKEND_IMAGE}:latest
                    """
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
                        sh """
                            docker push ${BACKEND_IMAGE}:${env.BUILD_NUMBER}
                            docker push ${BACKEND_IMAGE}:latest
                        """
                    }
                }
            }
        }

        stage('Run Model Test') {
            agent {
                docker {
                    image 'python:3.10'
                    args '-u root'
                }
            }
            steps {
                dir('maskdetectorbackend') {
                    sh 'pip install --no-cache-dir -r requirements.txt'
                    sh 'python -m unittest discover -s . -p "test_*.py" || true'
                }
            }
        }

        stage('Deploy to Kubernetes') {
            agent any
            steps {
                script {
                    sh '''
                        ansible-galaxy collection install kubernetes.core
                        pip install kubernetes
                        ansible-playbook -i ansible/inventory.yml ansible/deploy.yaml --vault-password-file vault_pass.txt
                    '''
                }
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