# EC2 Setup

Use these ports:

- Backend: `9000`
- Frontend: `5173`
- Jenkins: `9090`
- PostgreSQL: `5432` internal only

After cloning on EC2, run this from the repo root:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin git
sudo usermod -aG docker $USER
newgrp docker

docker compose up -d --build
```

Open:

- `http://<EC2_PUBLIC_IP>:5173`
- `http://<EC2_PUBLIC_IP>:9000`

For Jenkins, use `http://<EC2_PUBLIC_IP>:9090` and run the job that uses `Jenkinsfile`.
