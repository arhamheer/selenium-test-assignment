pipeline {
  agent any
  triggers { githubPush() }
  
  environment {
    COMPOSE_FILE = 'docker-compose.yml'
    POSTGRES_PASSWORD = 'taskflow123'
    JWT_SECRET_KEY = 'secret'
    TEST_IMAGE = 'taskflow-selenium-tests'
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Clean & Start Stack') {
      steps {
        sh 'docker compose -f $COMPOSE_FILE down --remove-orphans || true'
        sh 'POSTGRES_PASSWORD=${POSTGRES_PASSWORD} JWT_SECRET_KEY=${JWT_SECRET_KEY} docker compose -f $COMPOSE_FILE up -d --build --force-recreate'
      }
    }

    stage('Run Selenium Tests') {
      steps {
        sh 'mkdir -p reports'
        sh 'docker build -f Dockerfile.selenium-tests -t $TEST_IMAGE .'
        sh """
          timeout 300 docker run --rm --network host \
            -e TASKFLOW_API_URL=http://127.0.0.1:9000 \
            -e TASKFLOW_UI_URL=http://127.0.0.1:5173 \
            -e TASKFLOW_WAIT_SECONDS=8 \
            -e TASKFLOW_SHORT_WAIT=3 \
            -e CHROME_BINARY=/usr/bin/chromium \
            -v $WORKSPACE:/workspace -w /workspace \
            --shm-size=2g $TEST_IMAGE \
            python3 -m pytest tests/selenium -q --junitxml=reports/selenium-report.xml || true
        """
        junit testResults: 'reports/selenium-report.xml', allowEmptyResults: false
        archiveArtifacts artifacts: 'reports/selenium-report.xml', fingerprint: true
      }
    }
  }

  post {
    always {
      sh 'docker compose -f $COMPOSE_FILE down --remove-orphans || true'
      
      script {
        def pusherEmail = sh(script: "git log -1 --pretty=%ae", returnStdout: true).trim()
        if (pusherEmail?.contains("@")) {
          emailext(
            to: pusherEmail,
            subject: "TaskFlow Jenkins: ${currentBuild.currentResult}",
            body: """
              Build Result: ${currentBuild.currentResult}
              Job: ${env.JOB_NAME}
              Build: ${env.BUILD_NUMBER}
              URL: ${env.BUILD_URL}
              Test Report: ${env.BUILD_URL}testReport
            """,
            attachLog: true
          )
        } else {
          echo "No valid pusher email found"
        }
      }
    }
  }
}