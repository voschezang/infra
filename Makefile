
install:
	python3 -m pip install -r requirements.txt
	brew install ollama pyenv
	ollama pull gemma4:e2b
	# ollama pull gemma4:e4b
	# ollama pull llama3.1:8b
	# k8
	brew install minikube
	brew install helm
	helm repo add langfuse https://langfuse.github.io/langfuse-k8s
	helm repo update
