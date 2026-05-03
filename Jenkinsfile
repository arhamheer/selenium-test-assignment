pipeline {
  agent any

  triggers {
    githubPush()
  }

  environment {
    COMPOSE_FILE = 'docker-compose.yml'
    POSTGRES_PASSWORD = 'taskflow123'
    JWT_SECRET_KEY = 'secret'
    TEST_IMAGE = 'taskflow-selenium-tests'
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Clean & Start Stack') {
      steps {
        sh '''#!/bin/bash
set +e
docker compose -f $COMPOSE_FILE down --remove-orphans || true
docker ps -aq --filter "name=taskflow" | xargs -r docker rm -f || true
docker network ls --format '{{.Name}}' | grep '^taskflow' | xargs -r docker network rm || true
set -e
POSTGRES_PASSWORD=${POSTGRES_PASSWORD} JWT_SECRET_KEY=${JWT_SECRET_KEY} docker compose -f $COMPOSE_FILE up -d --build --force-recreate
sleep 5
docker ps
'''
      }
    }

    stage('Run Selenium Tests') {
      steps {
        sh 'mkdir -p $WORKSPACE/reports'
        sh 'docker build -f Dockerfile.selenium-tests -t $TEST_IMAGE .'
        
        sh '''#!/bin/bash
set +e
docker run --rm --network host \
  -e TASKFLOW_API_URL=http://127.0.0.1:9000 \
  -e TASKFLOW_UI_URL=http://127.0.0.1:5173 \
  -e TASKFLOW_WAIT_SECONDS=8 \
  -e TASKFLOW_SHORT_WAIT=3 \
  -e CHROME_BINARY=/usr/bin/chromium \
  -v $WORKSPACE:/workspace \
  -w /workspace \
  --shm-size=2g $TEST_IMAGE \
  bash -c "python3 -m pytest tests/selenium -v --tb=short --junitxml=reports/selenium-report.xml 2>&1 | tee reports/test-output.txt; echo 'PYTEST_EXIT_CODE=$?'"
set -e
'''
        
        // Verify files exist for debugging
        sh 'ls -la $WORKSPACE/reports/ || echo "reports dir missing"'
        sh 'wc -l $WORKSPACE/reports/test-output.txt || echo "test-output.txt missing"'
        
        junit testResults: 'reports/selenium-report.xml', allowEmptyResults: false
        archiveArtifacts artifacts: 'reports/*', fingerprint: true
      }
    }
  }

  post {
    always {
      script {
        def pusherEmail = sh(script: "git log -1 --pretty=%ae", returnStdout: true).trim()
        def committerName = sh(script: "git log -1 --pretty=%an", returnStdout: true).trim()

        // Read test output
        def testOutput = "No detailed test output available."
        def outputFile = "${env.WORKSPACE}/reports/test-output.txt"
        
        echo "Looking for test output at: ${outputFile}"
        
        if (fileExists(outputFile)) {
          testOutput = readFile(outputFile)
          echo "Found test output, length: ${testOutput.length()}"
          if (testOutput.length() > 6000) {
            testOutput = testOutput.take(6000) + "\n\n... [output truncated]"
          }
        } else {
          echo "Test output file not found at ${outputFile}"
        }

        // Validate email
        def isValidEmail = pusherEmail?.contains("@") \
          && !pusherEmail.contains("example.com") \
          && !pusherEmail.contains("test.com") \
          && !pusherEmail.contains("localhost") \
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
Timestamp:  ${new Date().format('yyyy-MM-dd HH:mm:ss z', TimeZone.getTimeZone('Asia/Karachi'))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TEST RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

${testOutput}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Jenkins: ${env.BUILD_URL}
Test Report (login required): ${env.BUILD_URL}testReport
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
