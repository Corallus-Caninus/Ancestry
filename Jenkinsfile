// NOTE: BUILT WITH KUBERNETES JENKINS PLUGIN
//       REQUIRES SERVICE

// TODO: parallelize tests branch only, cant fork from build branch
//       need dockerfile
pipeline {
    agent any
    stages {
        stage('prepare'){
            parallel serveBranch: {
                podTemplate(
                containers: [
                    containerTemplate(
                    name: 'ancestral-server',
                    image: 'python:3.8.5-slim-buster',
                    ttyEnabled: true,
                    command: 'cat'),
                ],
                label: 'ancestry-server'
                ) {
                    //TODO: scale out unittests on several pods to prototype yaml deployment structure over kubernetes.
                    node('ancestry-server') {
                        container('ancestral-server') {
                            stage('Build') {
                                //TODO: move this into docker image. Jenkins doesnt have
                                //      layered multistage build.
                                //git 'https://github.com/Corallus-Caninus/Nodal_NEAT.git' .
                                sh 'apt update'
                                sh 'apt install git -y'
                                sh 'git clone https://github.com/Corallus-Caninus/Nodal_NEAT.git Nodal_NEAT'
                                sh 'git clone https://github.com/Corallus-Caninus/Ancestry.git Ancestry'
                                // sh 'apt install build-essential -y'
                                sh 'pip install ./Nodal_NEAT'
                                sh 'pip install ./Ancestry'
                            }
                        }
                        stage('Serve') {
                            container('ancestral-server') {
                                dir('./Ancestry') {
                                    // TODO: call nose with JUnit reporting
                                    // TODO: call server here, unittests will be performed from the client
                                    //       since RoM object is shared this is fine.
                                    // sh 'python -m unittest'
                                    sh 'python ./pipeline/server.py &'
                                }
                            }
                        }
                    }
                }
            }, clientBranch: {
                // NOTE: this only scales out one client. a further pipeline CD implementation would have n clients.
                //       all unittests assume a RoM manager is serving shared objects.
                podTemplate(
                containers: [
                    containerTemplate(
                    name: 'ancestral-client',
                    image: 'python:3.8.5-slim-buster',
                    ttyEnabled: true,
                    command: 'cat'),
                ],
                label: 'ancestry-client'
                //label: 'ancestry-pipeline'
                ) {
                    //TODO: scale out unittests on several pods to prototype yaml deployment structure over kubernetes.
                    node('ancestry-client') {
                        container('ancestral-client') {
                            stage('Build') {
                                //TODO: move this into docker image. Jenkins doesnt have
                                //      layered multistage build.
                                //git 'https://github.com/Corallus-Caninus/Nodal_NEAT.git' .
                                sh 'apt update'
                                sh 'apt install git -y'
                                sh 'git clone https://github.com/Corallus-Caninus/Nodal_NEAT.git Nodal_NEAT'
                                sh 'git clone https://github.com/Corallus-Caninus/Ancestry.git Ancestry'
                                // sh 'apt install build-essential -y'
                                sh 'pip install ./Nodal_NEAT'
                                sh 'pip install ./Ancestry'
                            }
                        }
                    }
                }
            },
            failFast: false
        }
        stage('Test') {
            node('ancestry-client') {
                container('ancestral-client') {
                    dir('./Ancestry') {
                        // TODO: call nose with JUnit reporting
                        sh 'python -m unittest'
                    }
                }
            }
        }
    }
}