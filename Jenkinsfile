pipeline {
  agent any

  triggers {
    githubPush()
  }

  options {
    timestamps()
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

    stage('Start Stack') {
      steps {
        sh 'docker compose -f $COMPOSE_FILE down --remove-orphans || true'
        sh 'POSTGRES_PASSWORD=${POSTGRES_PASSWORD} JWT_SECRET_KEY=${JWT_SECRET_KEY} docker compose -f $COMPOSE_FILE up -d --build --force-recreate'
      }
    }

    stage('Run Selenium Tests') {
      steps {
        sh 'docker build -f Dockerfile.selenium-tests -t $TEST_IMAGE .'
        sh 'docker run --rm --network host -e TASKFLOW_API_URL=http://127.0.0.1:9000 -e TASKFLOW_UI_URL=http://127.0.0.1:5173 -e TASKFLOW_WAIT_SECONDS=30 -e CHROME_BINARY=/usr/bin/chromium -v $WORKSPACE:/workspace -w /workspace --shm-size=2g $TEST_IMAGE'
      }
    }

    stage('Health Check') {
      steps {
        sh 'curl -fsS http://localhost:5173/ --retry 5 --retry-delay 2'
        sh 'curl -fsSI http://localhost:9000/'
      }
    }
  }

  post {
    always {
      script {
        def pusherEmail = sh(script: "git log -1 --pretty=%ae", returnStdout: true).trim()
        mail(
          to: pusherEmail,
          subject: "TaskFlow Jenkins result: ${currentBuild.currentResult}",
          body: "Build result: ${currentBuild.currentResult}\nJob: ${env.JOB_NAME}\nBuild: ${env.BUILD_NUMBER}\nURL: ${env.BUILD_URL}"
        )
      }
    }
  }
}
