pipeline {
  agent any

  triggers {
    githubPush()
  }

  options {
    timestamps()
  }

  parameters {
    string(name: 'PUBLIC_IP', defaultValue: '35.170.34.8', description: 'EC2 Elastic IP used by frontend API URL')
  }
  
  environment {
    COMPOSE_FILE = 'docker-compose.yml'
    POSTGRES_PASSWORD = 'taskflow123'
    JWT_SECRET_KEY = 'secret'
    DOCKERHUB_USERNAME = 'arhamheer'
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build Backend Image') {
      steps {
        sh 'docker build -t ${DOCKERHUB_USERNAME}/taskflow-backend:part1 ./backend'
      }
    }

    stage('Build Frontend Image') {
      steps {
        sh 'docker build --no-cache --pull --build-arg VITE_API_URL=http://${PUBLIC_IP}:9000 -t ${DOCKERHUB_USERNAME}/taskflow-frontend:part2 ./frontend'
      }
    }

    stage('Push Part2 Images') {
      steps {
        sh 'docker push ${DOCKERHUB_USERNAME}/taskflow-backend:part1'
        sh 'docker push ${DOCKERHUB_USERNAME}/taskflow-frontend:part2'
      }
    }

    stage('Deploy Part2 Stack') {
      steps {
        sh 'docker compose -f $COMPOSE_FILE down --remove-orphans || true'
        sh 'PUBLIC_IP=${PUBLIC_IP} POSTGRES_PASSWORD=${POSTGRES_PASSWORD} JWT_SECRET_KEY=${JWT_SECRET_KEY} VITE_API_URL=http://${PUBLIC_IP}:9000 docker compose -f $COMPOSE_FILE up -d --build --force-recreate'
      }
    }

    stage('Health Check') {
      steps {
        sh 'sleep 10 && curl -fsS http://localhost:5173/ --retry 5 --retry-delay 2'
        sh 'curl -fsSI http://localhost:9000/'
      }
    }
  }
}
