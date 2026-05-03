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
      def committerName = sh(script: "git log -1 --pretty=%an", returnStdout: true).trim()
      
      // Read test output if available
      def testOutput = "No detailed test output available."
      if (fileExists('reports/test-output.txt')) {
        testOutput = readFile('reports/test-output.txt')
        if (testOutput.length() > 5000) {
          testOutput = testOutput.take(5000) + "\n\n... [output truncated]"
        }
      }
      
      // Validate email
      def isValidEmail = pusherEmail?.contains("@") \
        && !pusherEmail.contains("example.com") \
        && !pusherEmail.contains("test.com") \
        && pusherEmail.contains(".")
      
      if (isValidEmail) {
        emailext(
          to: pusherEmail,
          subject: "TaskFlow CI: ${currentBuild.currentResult} | Build #${env.BUILD_NUMBER}",
          body: """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TaskFlow CI/CD Test Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Build:      ${env.JOB_NAME} #${env.BUILD_NUMBER}
Status:     ${currentBuild.currentResult}
Commit:     ${sh(script: 'git log -1 --pretty=%h -s', returnStdout: true).trim()}
Author:     ${committerName} <${pusherEmail}>
Timestamp:  ${new Date().format('yyyy-MM-dd HH:mm:ss')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TEST RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

${testOutput}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Note: Full Jenkins console requires login.
This email contains the complete test report.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
          """,
          attachLog: true
        )
      } else {
        echo "Skipping email to invalid address: '${pusherEmail}'"
      }
    }
  }
}
}