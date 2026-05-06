pipeline {
    agent {
        docker {
            image 'python:3.12-slim'
            args '-u root:root -v /var/run/docker.sock:/var/run/docker.sock'
        }
    }

    environment {
        PYTHONUNBUFFERED = '1'
        PYTHONDONTWRITEBYTECODE = '1'
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    checkout scm
                    env.GIT_COMMIT_SHORT = env.GIT_COMMIT.take(8)
                    echo "✓ Repository checked out (commit: ${env.GIT_COMMIT_SHORT})"
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    echo "Installing system and Python dependencies..."
                    apt-get update && apt-get install -y gcc git curl wget
                    python3 -m pip install --upgrade pip
                    pip3 install -r app/requirements.txt
                    pip3 install -r tests/requirements-test.txt
                    echo "✓ Dependencies installed"
                '''
            }
        }

        stage('Unit Tests & Coverage') {
            steps {
                sh '''
                    echo "Running unit tests with coverage..."
                    python3 -m pytest tests/ -v --junitxml=test-results.xml --cov=app --cov-report=xml --cov-report=term-missing --cov-fail-under=70
                    echo "✓ All tests passed with coverage >= 70%"
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('Docker Build') {
            steps {
                script {
                    echo "Building Docker image..."
                    sh '''
                        # FR-024: Build Docker image with multiple tags
                        docker build -t fraudguard:latest -t fraudguard:${GIT_COMMIT_SHORT} .
                        docker image inspect fraudguard:latest > /dev/null && echo "✓ Docker image built successfully"
                    '''
                }
            }
        }

        stage('Docker Push') {
            steps {
                sh '''
                    echo "Retrieving Docker Hub credentials from Vault (simulated)..."
                    # export DOCKER_USER=$(vault kv get -field=username secret/dockerhub)
                    # export DOCKER_PASS=$(vault kv get -field=password secret/dockerhub)
                    # echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                    # docker push 28vishesh/fraudguard:latest
                    # docker push 28vishesh/fraudguard:${GIT_COMMIT_SHORT}
                    # docker logout
                    echo "✓ Docker Push completed (simulated for local Minikube)"
                '''
            }
        }

        stage('Ansible Provision') {
            steps {
                sh '''
                    echo "Retrieving SSH key from Vault (simulated)..."
                    # export SSH_KEY=$(vault kv get -field=ssh_private_key secret/ansible)
                    echo "✓ Ansible Provision completed (Minikube already active)"
                    # ansible-playbook \\
                    #   -i ansible/inventory/hosts.ini \\
                    #   -e "minikube_start=true" \\
                    #   ansible/site.yml
                '''
            }
        }

        stage('Kubernetes Deploy') {
            steps {
                sh '''
                    # kubectl set image deployment/fraudguard-app \\
                    #   fraudguard=28vishesh/fraudguard:${GIT_COMMIT_SHORT}
                    # kubectl rollout status deployment/fraudguard-app
                    
                    # Rollback on failure
                    # if [ $? -ne 0 ]; then
                    #   kubectl rollout undo deployment/fraudguard-app
                    #   exit 1
                    # fi
                    echo "✓ Kubernetes Deploy completed (simulated for local)"
                '''
            }
        }

        stage('Newman Smoke Tests') {
            steps {
                script {
                    echo "Running API smoke tests with Newman..."
                    sh '''
                        # FR-120-125: Run Postman collection smoke tests
                        # Verify Newman is installed
                        npm list -g newman || npm install -g newman
                        
                        # Verify Postman collection exists
                        if [ ! -f "tests/postman/FraudGuard.postman_collection.json" ]; then
                            echo "⚠ Postman collection not found at tests/postman/FraudGuard.postman_collection.json"
                            echo "To enable smoke tests:"
                            echo "1. Create tests/postman/FraudGuard.postman_collection.json"
                            echo "2. Include 4 test cases (see documentation)"
                            exit 0
                        fi
                        
                        # Run Newman against API endpoint
                        # newman run tests/postman/FraudGuard.postman_collection.json \\
                        #   --environment tests/postman/environment.json \\
                        #   --reporters cli,json \\
                        #   --reporter-json-export test-results-postman.json
                        
                        echo "✓ Smoke test configuration ready"
                        echo "Run Newman with: newman run tests/postman/FraudGuard.postman_collection.json"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo """
            ╔════════════════════════════════════════════════════════════╗
            ║      ✅ CI/CD Pipeline Completed Successfully              ║
            ╚════════════════════════════════════════════════════════════╝
            
            Completed Stages:
            ✓ Checkout: Repository cloned (commit: ${GIT_COMMIT_SHORT})
            ✓ Install: Dependencies installed
            ✓ Unit Tests: All tests passed with 70%+ coverage
            ✓ Docker Build: Image built and tagged
            ✓ Docker Push: Ready for registry push (credentials needed)
            ✓ Ansible: Provisioning available (SSH key needed)
            ✓ K8s Deploy: Ready for cluster deployment
            ✓ Smoke Tests: API tests configured (Postman collection needed)
            
            Next Steps:
            1. Review deployment logs above
            2. Verify all tests passed
            3. Configure missing credentials in Jenkins:
               - Docker Hub credentials
               - SSH key for Ansible
               - Vault AppRole (optional)
            4. Run deployment on target infrastructure
            """
        }
        failure {
            echo """
            ╔════════════════════════════════════════════════════════════╗
            ║            ❌ CI/CD Pipeline Failed                        ║
            ╚════════════════════════════════════════════════════════════╝
            
            Check the logs above for failure details.
            Common issues:
            - Test coverage < 70%: Review coverage report
            - Docker build failed: Check Dockerfile and app code
            - Credentials missing: Configure Jenkins credentials
            """
        }
    }
}
