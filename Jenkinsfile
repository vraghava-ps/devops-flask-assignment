pipeline {
    agent any

    environment {
        AWS_REGION      = 'ap-south-1'
        ECR_REPOSITORY  = 'flask-devops-assessment'
        ECS_CLUSTER     = 'flask-assessment-cluster'
        STAGING_SERVICE = 'flask-staging'
        PROD_SERVICE    = 'flask-production'
        IMAGE_TAG       = "${BUILD_NUMBER}"
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install -r requirements-dev.txt
                    pytest -v --junitxml=test-results.xml
                '''
            }
        }

        stage('Dependency Security Scan') {
            steps {
                sh '''
                    . .venv/bin/activate
                    bandit -r app
                    safety check -r requirements.txt
                '''
            }
        }

        stage('Build Docker Image') {
            when {
                branch 'main'
            }
            steps {
                sh 'docker build -t ${ECR_REPOSITORY}:${IMAGE_TAG} .'
            }
        }

        stage('Container Vulnerability Scan') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    trivy image --exit-code 1 --severity HIGH,CRITICAL \
                    ${ECR_REPOSITORY}:${IMAGE_TAG}
                '''
            }
        }

        stage('Push to ECR') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
                    ECR_URI=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY

                    aws ecr get-login-password --region $AWS_REGION | \
                    docker login --username AWS --password-stdin $ECR_URI

                    docker tag $ECR_REPOSITORY:$IMAGE_TAG $ECR_URI:$IMAGE_TAG
                    docker tag $ECR_REPOSITORY:$IMAGE_TAG $ECR_URI:latest

                    docker push $ECR_URI:$IMAGE_TAG
                    docker push $ECR_URI:latest
                '''
            }
        }

        stage('Deploy Staging') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    aws ecs update-service \
                      --cluster $ECS_CLUSTER \
                      --service $STAGING_SERVICE \
                      --force-new-deployment \
                      --region $AWS_REGION

                    aws ecs wait services-stable \
                      --cluster $ECS_CLUSTER \
                      --services $STAGING_SERVICE \
                      --region $AWS_REGION
                '''
            }
        }

        stage('Production Approval') {
            when {
                branch 'main'
            }
            steps {
                input message: 'Approve production deployment?', ok: 'Deploy'
            }
        }

        stage('Deploy Production') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    aws ecs update-service \
                      --cluster $ECS_CLUSTER \
                      --service $PROD_SERVICE \
                      --force-new-deployment \
                      --region $AWS_REGION

                    aws ecs wait services-stable \
                      --cluster $ECS_CLUSTER \
                      --services $PROD_SERVICE \
                      --region $AWS_REGION
                '''
            }
        }
    }

    post {
        always {
            junit 'test-results.xml'
            cleanWs()
        }

        failure {
            withCredentials([
                string(credentialsId: 'slack-webhook-url', variable: 'SLACK_WEBHOOK')
            ]) {
                sh '''
                    curl -X POST -H 'Content-type: application/json' \
                    --data "{\"text\":\"Jenkins build failed: $JOB_NAME #$BUILD_NUMBER - $BUILD_URL\"}" \
                    $SLACK_WEBHOOK
                '''
            }
        }
    }
}