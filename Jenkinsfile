pipeline {
    agent none
    environment {
        DOCKERHUB_CREDENTIALS = credentials('DockerHubCred')
        DOCKERHUB_USERNAME = 'navalbisht444'
        FRONTEND_REPO_URL = 'https://github.com/Naval-Bisht/imagedetector'
        BACKEND_REPO_URL = 'https://github.com/Naval-Bisht/imagedetectorbackend.git' // Adjust to your backend repo
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
                    // Checkout frontend repository
                    checkout([$class: 'GitSCM',
                              branches: [[name: '*/main']],
                              userRemoteConfigs: [[url: "${FRONTEND_REPO_URL}"]]])
                    // Checkout backend repository into a subdirectory
                    dir('backend-repo') {
                        checkout([$class: 'GitSCM',
                                  branches: [[name: '*/main']],
                                  userRemoteConfigs: [[url: "${BACKEND_REPO_URL}"]]])
                    }
                }
            }
        }

        // Frontend Pipeline
        stage('Build Frontend Docker Image') {
            agent any
            steps {
                dir('maskdetector') {
                    sh "docker build -t ${FRONTEND_IMAGE}:${env.BUILD_NUMBER} ."
                    sh "docker tag ${FRONTEND_IMAGE}:${env.BUILD_NUMBER} ${FRONTEND_IMAGE}:latest"
                }
            }
        }

        stage('Verify Frontend Docker Image') {
            agent any
            steps {
                sh "docker run --rm ${FRONTEND_IMAGE}:${env.BUILD_NUMBER} nginx -t"
            }
        }

        stage('Push Frontend Docker Image') {
            agent any
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', DOCKERHUB_CREDENTIALS) {
                        sh "docker push ${FRONTEND_IMAGE}:${env.BUILD_NUMBER}"
                        sh "docker push ${FRONTEND_IMAGE}:latest"
                    }
                }
            }
        }

        // Backend Pipeline
        stage('Build Backend Docker Image') {
            agent any
            steps {
                dir('backend-repo/maskdetectorbackend') { // Adjust to your backend directory
                    sh "docker build -t ${BACKEND_IMAGE}:${env.BUILD_NUMBER} ."
                    sh "docker tag ${BACKEND_IMAGE}:${env.BUILD_NUMBER} ${BACKEND_IMAGE}:latest"
                }
            }
        }

        stage('Verify Backend Docker Image') {
            agent any
            steps {
                sh "docker run --rm ${BACKEND_IMAGE}:${env.BUILD_NUMBER} gunicorn --check-config app:app"
            }
        }

        stage('Push Backend Docker Image') {
            agent any
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', DOCKERHUB_CREDENTIALS) {
                        sh "docker push ${BACKEND_IMAGE}:${env.BUILD_NUMBER}"
                        sh "docker push ${BACKEND_IMAGE}:latest"
                    }
                }
            }
        }

        stage('Run Model Test') {
            agent {
                docker {
                    image "${BACKEND_IMAGE}:${env.BUILD_NUMBER}"
                    args '--user root' // Run as root for test execution
                }
            }
            steps {
                dir('maskdetectorbackend') {
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
            node('any') { // Use 'any' or a valid node label
                script {
                    sh "docker rmi ${FRONTEND_IMAGE}:${env.BUILD_NUMBER} ${FRONTEND_IMAGE}:latest || true"
                    sh "docker rmi ${BACKEND_IMAGE}:${env.BUILD_NUMBER} ${BACKEND_IMAGE}:latest || true"
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