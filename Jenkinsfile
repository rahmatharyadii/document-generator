pipeline {
    agent {
        node {
            label 'master'
        }
    }

    environment {
        APP_NAME = 'document-generator'
        APP_VERSION = '0.1'
        GROUP_NAME = 'document-generator'
        YAML_NAME = 'docker-compose'
        HARBOR_JTL_REPO_URL = 'jtl-tkgiharbor.hq.bni.co.id'
        HARBOR_JTL_PROJECT_NAME = 'mnd-dev'
        NO_PROXY = '*.bni.co.id'
        HARBOR_JTL_CREDENTIAL_ID = 'afec3c64-7cde-4139-8498-75960bcb1fa8'
        OCP_CLUSTER_API = 'https://api.delta.ocp.hq.bni.co.id:6443'
        OCP_NAMESPACE_NAME = 'kkp-digit-dev'
        OCP_CREDENTIAL_ID = 'a002f424-c7a2-45cb-b7c1-10a505ca89e0'
    }

    options {
        disableConcurrentBuilds()
        timeout(time: 1, unit: 'HOURS')
    }


    stages {

        stage('Build and push') {
            steps {
                script {
                    // Build Docker Image
                    echo "----------- Build -----------"
                    sh """
                        docker build -f Dockerfile -t ${HARBOR_JTL_REPO_URL}/${HARBOR_JTL_PROJECT_NAME}/${APP_NAME}:${APP_VERSION} .
                    """

                    // Login to Harbor
                    echo "----------- Login Harbor -----------"
                    withCredentials([usernamePassword(credentialsId: "${HARBOR_JTL_CREDENTIAL_ID}", usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
                        sh "docker login -u $USERNAME -p $PASSWORD ${HARBOR_JTL_REPO_URL}"
                        sh "docker push ${HARBOR_JTL_REPO_URL}/${HARBOR_JTL_PROJECT_NAME}/${APP_NAME}:${APP_VERSION}"
                    }
                }
            }
        }

        stage('Update docker-compose') {
            steps {
                script {
                    def yamlFile = "${YAML_NAME}.yml"
                    if (fileExists(yamlFile)) {
                        echo "File ${yamlFile} ditemukan. Memulai proses update."

                        // Update VERSION dan APP_NAME dalam YAML
                        sh """
                        yq e '
                        (.parameters[] | select(.name == "IMAGE_NAME").value) = "${HARBOR_JTL_REPO_URL}/${HARBOR_JTL_PROJECT_NAME}/${APP_NAME}:${APP_VERSION}"
                        ' -i "${yamlFile}"
                        """

                        echo "File ${yamlFile} berhasil diperbarui. Berikut isi file setelah update:"
                        sh "cat ${yamlFile}"
                    } else {
                        error "File ${yamlFile} tidak ditemukan!"
                    }
                }
            }
        }


        stage('SSH Login') {
            steps {
                script {
                    echo "----------- Login SSH -----------"
                    // Install sshpass if needed (for password-based auth)
                    sh 'which sshpass || (apt-get update -qq && apt-get install -y sshpass)'
                    
                    // Execute SSH with password
                    withEnv(['SSHPASS=soadev']) {
                        sh '''
                            sshpass -e ssh \
                                -o StrictHostKeyChecking=no \
                                -o PubkeyAuthentication=no \
                                soadev@192.168.65.112 \
                                "echo SSH login successful"
                        '''
                    }
                }
            }
        }


        stage('Deploy') {
            steps {
                script {
                    // Deploy to Docker
                    // Login to Harbor
                    echo "----------- Login Harbor -----------"
                    withCredentials([usernamePassword(credentialsId: "${HARBOR_JTL_CREDENTIAL_ID}", usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
                        sh "docker login -u $USERNAME -p $PASSWORD ${HARBOR_JTL_REPO_URL}"
                        sh "docker stack deploy --compose-file docker-compose.yml ${APP_NAME} --with-registry-auth"
                    }
                    // Clean Up
                    echo "----------- Clean Up -----------"
                    sh "docker image rm -f ${HARBOR_JTL_REPO_URL}/${HARBOR_JTL_PROJECT_NAME}/${APP_NAME}:${APP_VERSION} || true"
                }
            }
        }

    }

    post {
        success {
            script {
            echo "Build SUCCESS"
                cleanWs()
            }
        }
        failure {
            script {
            echo "Build FAILURE"
                cleanWs()
            }
        }
        aborted {
            script {
                echo "Build Aborted"
                cleanWs()
            }
        }
    }
}
