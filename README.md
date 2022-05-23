# kPhobos

OAI-UE-nFAPI deployment on Kubernetes

#### Build Docker image
```bash
docker build -t j0lama/<image name>:latest .
```

#### Push Docker image to DockerHub
```bash
docker image push j0lama/<image name>:latest
```

#### Deploy Pod
```bash
kubectl run <pod name> --rm -i --tty --privileged --image j0lama/<image name>:latest -- bash
```

#### Run bash inside pod
```bash
kubectl exec -ti <pod name> -- bash
```