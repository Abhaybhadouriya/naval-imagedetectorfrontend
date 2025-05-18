pipeline {
    agent none
    environment {
        DOCKERHUB_CREDENTIALS = credentials('DockerHubCred')
        DOCKERHUB_USERNAME = 'navalbisht444'
        REPO_URL = 'https://github.com/Naval-Bisht/imagedetectorfrontend.git'
        EMAIL_RECIPIENT = 'navalbisht444@gmail.com'
        FRONTEND_IMAGE = "${DOCKERHUB_USERNAME}/maskdetector"
        BACKEND_IMAGE = "${DOCKERHUB_USERNAME}/maskdetectorbackend"
    }
    triggers {
        githubPush()
    }
    stages {
        stage('Checkout') {
            agent any
            steps {
                script {
                    git branch: 'main', url: "${REPO_URL}"
                }
            }
        }

        // Frontend Pipeline
        stage('Build Frontend Docker Image') {
            agent any
            steps {
                script {
                    dir('frontend') {
                        docker.build("${FRONTEND_IMAGE}", '.')
                    }
                }
            }
        }

        stage('Verify Frontend Docker Image') {
            agent any
            steps {
                script {
                    sh "docker run --rm ${FRONTEND_IMAGE} npm test || true"
                }
            }
        }

        stage('Push Frontend Docker Image') {
            agent any
            steps {
                script {
                    docker.withRegistry('', 'DockerHubCred') {
                        sh "docker tag ${FRONTEND_IMAGE} ${FRONTEND_IMAGE}:latest"
                        sh "docker push ${FRONTEND_IMAGE}:latest"
                    }
                }
            }
        }

        // Backend Pipeline
        stage('Build Backend Docker Image') {
            agent any
            steps {
                script {
                    dir('backend') {
                        docker.build("${BACKEND_IMAGE}", '.')
                    }
                }
            }
        }

        stage('Verify Backend Docker Image') {
            agent any
            steps {
                script {
                    sh "docker run --rm ${BACKEND_IMAGE} python -m unittest discover || true"
                }
            }
        }

        stage('Push Backend Docker Image') {
            agent any
            steps {
                script {
                    docker.withRegistry('', 'DockerHubCred') {
                        sh "docker tag ${BACKEND_IMAGE} ${BACKEND_IMAGE}:latest"
                        sh "docker push ${BACKEND_IMAGE}:latest"
                    }
                }
            }
        }

        stage('Run Model Test') {
            agent any
            steps {
                script {
                    sh 'python test.py'
                }
            }
        }

        stage('Run Ansible Playbook') {
            agent any
            steps {
                script {
                    ansiblePlaybook(
                        playbook: 'deploy.yml',
                        inventory: 'inventory',
                        extras: '--vault-password-file vault_pass.txt'
                    )
                }
            }
        }
    }

    post {
        always {
            node('master') {
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














































// pipeline {
//     agent none
//     environment {
//         DOCKERHUB_CREDENTIALS = credentials('DockerHubCred') // Docker Hub credentials ID
//         DOCKERHUB_USERNAME = 'navalbisht444' // Your Docker Hub username
//         REPO_URL = 'https://github.com/Naval-Bisht/imagedetectorfrontend.git'
//         EMAIL_RECIPIENT = 'navalbisht444@gmail.com' // Your email
//         FRONTEND_IMAGE = "${DOCKERHUB_USERNAME}/maskdetector"
//         BACKEND_IMAGE = "${DOCKERHUB_USERNAME}/maskdetectorbackend"
//     }
//     stages {
//         stage('Checkout Code') {
//             agent any
//             steps {
//                 echo 'Checking out code...'
//                 checkout([$class: 'GitSCM',
//                           branches: [[name: '*/main']],
//                           userRemoteConfigs: [[url: "${REPO_URL}",
//                                               credentialsId: 'e6f4d547-b3b9-4c0b-9dea-a5d41ccbc676']]])
//             }
//         }
//         stage('Build Frontend Docker Image') {
//             agent {
//                 docker {
//                     image 'node:16-alpine'
//                     args '-u root'
//                 }
//             }
//             steps {
//                 echo 'Building frontend Docker image...'
//                 dir('maskdetector') {
//                     sh 'npm install || { echo "npm install failed"; exit 1; }'
//                     sh 'npm run build || { echo "Build failed"; exit 1; }'
//                     sh """
//                         docker build -t ${FRONTEND_IMAGE}:${env.BUILD_NUMBER} . || { echo "Docker build failed"; exit 1; }
//                         docker tag ${FRONTEND_IMAGE}:${env.BUILD_NUMBER} ${FRONTEND_IMAGE}:latest
//                     """
//                 }
//             }
//         }
//         stage('Verify Frontend Docker Image') {
//             agent {
//                 docker {
//                     image 'docker:20.10'
//                     args '-v /var/run/docker.sock:/var/run/docker.sock -u root'
//                 }
//             }
//             steps {
//                 echo 'Verifying frontend Docker image...'
//                 sh """
//                     docker run --rm ${FRONTEND_IMAGE}:${env.BUILD_NUMBER} nginx -v || { echo "Image verification failed"; exit 1; }
//                 """
//             }
//         }
//         stage('Build Backend Docker Image') {
//             agent {
//                 docker {
//                     image 'python:3.11-slim'
//                     args '-u root'
//                 }
//             }
//             steps {
//                 echo 'Building backend Docker image...'
//                 dir('maskdetectorbackend') {
//                     sh 'pip install --no-cache-dir -r requirements.txt || { echo "pip install failed"; exit 1; }'
//                     sh """
//                         docker build -t ${BACKEND_IMAGE}:${env.BUILD_NUMBER} . || { echo "Docker build failed"; exit 1; }
//                         docker tag ${BACKEND_IMAGE}:${env.BUILD_NUMBER} ${BACKEND_IMAGE}:latest
//                     """
//                 }
//             }
//         }
//         stage('Verify Backend Docker Image') {
//             agent {
//                 docker {
//                     image 'docker:20.10'
//                     args '-v /var/run/docker.sock:/var/run/docker.sock -u root'
//                 }
//             }
//             steps {
//                 echo 'Verifying backend Docker image...'
//                 sh """
//                     docker run --rm ${BACKEND_IMAGE}:${env.BUILD_NUMBER} python --version || { echo "Image verification failed"; exit 1; }
//                 """
//             }
//         }
//         stage('Test Backend Model') {
//             agent {
//                 docker {
//                     image 'python:3.11-slim'
//                     args '-u root'
//                 }
//             }
//             steps {
//                 echo 'Running model tests...'
//                 dir('maskdetectorbackend') {
//                     sh 'pip install --no-cache-dir -r requirements.txt'
//                     sh 'python test_model.py || { echo "Model tests failed"; exit 1; }'
//                 }
//             }
//         }
//         stage('Push Docker Images') {
//             agent {
//                 docker {
//                     image 'docker:20.10'
//                     args '-v /var/run/docker.sock:/var/run/docker.sock -u root'
//                 }
//             }
//             steps {
//                 echo 'Pushing Docker images to Docker Hub...'
//                 sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_USERNAME --password-stdin || { echo "Docker login failed"; exit 1; }'
//                 sh """
//                     docker push ${FRONTEND_IMAGE}:${env.BUILD_NUMBER} || { echo "Frontend push failed"; exit 1; }
//                     docker push ${FRONTEND_IMAGE}:latest || { echo "Frontend push failed"; exit 1; }
//                     docker push ${BACKEND_IMAGE}:${env.BUILD_NUMBER} || { echo "Backend push failed"; exit 1; }
//                     docker push ${BACKEND_IMAGE}:latest || { echo "Backend push failed"; exit 1; }
//                 """
//             }
//         }
//         stage('Deploy to Kubernetes') {
//             agent any
//             steps {
//                 echo 'Running Ansible playbook for Kubernetes deployment...'
//                 dir('ansible') {
//                     sh '''
//                         ansible-galaxy collection install kubernetes.core
//                         pip3 install kubernetes
//                         ansible-playbook -i inventory.yml deploy.yaml || { echo "Kubernetes deployment failed"; exit 1; }
//                     '''
//                 }
//             }
//         }
//         stage('Verify Deployment') {
//             agent any
//             steps {
//                 echo 'Verifying Kubernetes deployment...'
//                 sh 'kubectl get pods -n default'
//                 sh 'kubectl get svc -n default'
//             }
//         }
//     }
//     post {
//         always {
//             node('') {
//                 echo 'Cleaning up Docker images...'
//                 sh """
//                     docker rmi ${FRONTEND_IMAGE}:${env.BUILD_NUMBER} || true
//                     docker rmi ${FRONTEND_IMAGE}:latest || true
//                     docker rmi ${BACKEND_IMAGE}:${env.BUILD_NUMBER} || true
//                     docker rmi ${BACKEND_IMAGE}:latest || true
//                 """
//                 cleanWs()
//             }
//         }
//         success {
//             node('') {
//                 echo 'Pipeline completed successfully!'
//                 mail to: "${EMAIL_RECIPIENT}",
//                      subject: "✅ Jenkins Pipeline Success: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
//                      body: "The pipeline ${env.JOB_NAME} #${env.BUILD_NUMBER} completed successfully.\nCheck the build at ${env.BUILD_URL}"
//             }
//         }
//         failure {
//             node('') {
//                 echo 'Pipeline failed!'
//                 mail to: "${EMAIL_RECIPIENT}",
//                      subject: "❌ Jenkins Pipeline Failure: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
//                      body: "The pipeline ${env.JOB_NAME} #${env.BUILD_NUMBER} failed.\nCheck the build at ${env.BUILD_URL}"
//             }
//         }
//     }
// }
