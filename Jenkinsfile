pipeline {
    agent none // No default agent; each stage must specify its own
    environment {
        DOCKERHUB_CREDENTIALS = credentials('DockerHubCred') // Docker Hub credentials ID
        DOCKERHUB_USERNAME = 'navalbisht444'
        REPO_URL = 'https://github.com/Naval-Bisht/imagedetectorfrontend.git'
        EMAIL_RECIPIENT = 'navalbisht444@gmail.com'
        FRONTEND_IMAGE = "${DOCKERHUB_USERNAME}/image-processing-frontend"
        BACKEND_IMAGE = "${DOCKERHUB_USERNAME}/image-processing-backend"
    }
    triggers {
        githubPush() // Trigger on GitHub push (ensure webhook is configured)
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
            agent any // Specify agent
            steps {
                script {
                    // Build and tag frontend image with build number and latest
                    frontendImage = docker.build("${FRONTEND_IMAGE}:${env.BUILD_NUMBER}", './maskdetector/')
                    sh "docker tag ${FRONTEND_IMAGE}:${env.BUILD_NUMBER} ${FRONTEND_IMAGE}:latest"
                }
            }
        }


        stage('Verify Frontend Docker Image') {
            agent any
            steps {
                script {
                    // Verify the frontend image (assuming Node.js-based frontend; adjust as needed)
                    sh """
                        docker run --rm ${FRONTEND_IMAGE}:${env.BUILD_NUMBER} node --version || echo 'Node.js not found; adjust verification command'
                    """
                }
            }
        }

        stage('Push Frontend Docker Image') {
            agent any
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'DockerHubCred') {
                        frontendImage.push("${env.BUILD_NUMBER}")
                        frontendImage.push('latest')
                    }
                }
            }
        }

        // Backend Pipeline
        stage('Build Backend Docker Image') {
            agent any
            steps {
                script {
                    // Build and tag backend image with build number and latest
                    backendImage = docker.build("${BACKEND_IMAGE}:${env.BUILD_NUMBER}", './maskdetectorbackend/')
                    sh "docker tag ${BACKEND_IMAGE}:${env.BUILD_NUMBER} ${BACKEND_IMAGE}:latest"
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
                        backendImage.push("${env.BUILD_NUMBER}")
                        backendImage.push('latest')
                    }
                }
            }
        }

        stage('Deployment using Ansible') {
            agent any
            steps {
                script {
                     sh 'chmod -R u+rwX /var/lib/jenkins/workspace/maskman_mini/ansible /var/lib/jenkins/workspace/maskman_mini/kubernetes'
                     withEnv(["ANSIBLE_HOST_KEY_CHECKING=False"]) {   
                    ansiblePlaybook(
                        playbook: 'ansible/deploy.yaml',
                        inventory: 'inventory'
                    )
                    }
                }
            }
        }

        stage('Verify Deployment') {
            agent any
            steps {
                script {
                    // Verify Kubernetes deployment
                    sh 'kubectl get pods -n default'
                    sh 'kubectl get svc -n default'
                }
            }
        }
    }

    post {
        always {
            node('any') { // Use 'any' instead of 'master' for flexibility
                script {
                    // Clean up Docker images
                    sh """
                        docker rmi ${FRONTEND_IMAGE}:${env.BUILD_NUMBER} || true
                        docker rmi ${FRONTEND_IMAGE}:latest || true
                        docker rmi ${BACKEND_IMAGE}:${env.BUILD_NUMBER} || true
                        docker rmi ${BACKEND_IMAGE}:latest || true
                    """
                    cleanWs() // Clean workspace
                }
                // Send email notification
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