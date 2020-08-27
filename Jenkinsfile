// NOTE: BUILT WITH KUBERNETES JENKINS PLUGIN
//       REQUIRES SERVICE
podTemplate(
containers: [
    containerTemplate(
    name: 'Ancestral_Server',
    image: 'python:3.8.5-slim-buster',
    ttyEnabled: true,
    command: 'cat'),
],
label: 'ancestry-pipeline'
) {
    //TODO: scale out unittests on several pods to prototype yaml deployment structure over kubernetes.
    node(POD_LABEL) {
        container('Ancestral_Server') {
            stage('Build') {
                //TODO: move this into docker image. Jenkins doesnt have
                //      layered multistage build.
                //git 'https://github.com/Corallus-Caninus/Nodal_NEAT.git' .
                sh 'apt update'
                sh 'apt install git -y'
                sh 'git clone https://github.com/Corallus-Caninus/Ancestry.git Ancestry'
                sh 'apt install build-essential -y'
                //TODO: this should be handled in setup.py
                sh 'pip install graphviz'
                sh 'pip install matplotlib'
                sh 'pip install ./Ancestry'
            }
        }
        stage('Serve') {
            container('Ancestral_Server') {
                dir('./Ancestry') {
                    // TODO: call nose with JUnit reporting
                    // TODO: call server here, unittests will be performed from the client
                    //       since RoM object is shared this is fine.
                    // sh 'python -m unittest'
                    sh 'python ./pipeline/server.py'
                }
            }
        }
    }
}

// NOTE: this only scales out one client. a further pipeline CD implementation would have n clients.
//       all unittests assume a RoM manager is serving shared objects.
podTemplate(
containers: [
    containerTemplate(
    name: 'Ancestral_Server',
    image: 'python:3.8.5-slim-buster',
    ttyEnabled: true,
    command: 'cat'),
],
label: 'ancestry-pipeline'
) {
    //TODO: scale out unittests on several pods to prototype yaml deployment structure over kubernetes.
    node(POD_LABEL) {
        container('Ancestral_Client') {
            stage('Build') {
                //TODO: move this into docker image. Jenkins doesnt have
                //      layered multistage build.
                //git 'https://github.com/Corallus-Caninus/Nodal_NEAT.git' .
                sh 'apt update'
                sh 'apt install git -y'
                sh 'git clone https://github.com/Corallus-Caninus/Ancestry.git Ancestry'
                sh 'apt install build-essential -y'
                //TODO: this should be handled in setup.py
                sh 'pip install graphviz'
                sh 'pip install matplotlib'
                sh 'pip install ./Ancestry'
            }
        }
        stage('Test') {
            container('Ancestral_Server') {
                dir('./Ancestry') {
                    // TODO: call nose with JUnit reporting
                    sh 'python -m unittest'
                }
            }
        }
    }
}
