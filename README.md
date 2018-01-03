# Demo k8s - che 

The following steps are intended to set up a demo configuration between Eclipse Che and Kubernetes via Juju. The final outcome is a Eclipse Che workspace which can deploy a python script to Kubernetes. 

## Prerequisites
You will need the following items in order to complete the guidelines:
 - Access to a Juju model / credentials
 - This repository cloned locally on your computer
 - Docker credentials
 - A public docker repository named `helloflask`

## Step 0: Complete the bundle configuration
In bundles directory you will find a Juju bundle named `k8s-che-bundle.yaml`, this bundle describes a set of configurations for your Juju model. 

Fill in your Juju credentials for the api charm.
```
      juju_password: #####
      juju_user: #####
```

## Step 1: Deploy the bundle
Make sure you are in the right model before deploying the bundle. You can check your current model via `juju status`. 
Then deploy via:
```
cd bundles
juju deploy k8s-che-bundle.yaml
```
You can monitor the deployment with `watch -c juju status --color`. When all applications are active (except the haproxy charm which will stay "unkown") the deployment is done.

## Step 2:  Upgrade Eclipse Che to the latest version
The Eclipse Che charm uses (at the time of writing) an older version. We'll upgrade to the latest build to get the newest features and bug fixes. 
```
juju ssh eclipse-che/0

docker stop $(docker ps -a -q) # Stop all docker containers
docker rm $(docker ps -a -q)   # Remove all docker containers
docker rmi $(docker images -q) # Remove all docker images

# The next command uses the IP address of the machine. Find this via juju status or if you are on the VMware cluster you can also find it via ifconfig under the ens192 interface. 
IP="X.X.X.X"

docker run -it --rm -v /var/run/docker.sock:/var/run/docker.sock -v /home/ubuntu/:/data -e CHE_HOST="$IP" -e CHE_DOCKER_IP_EXTERNAL="$IP" eclipse/che upgrade

# The following command will cause Che to bind the docker socket in every workspace. We need this to access the docker daemon on the host.
echo "che.workspace.volume=/var/run/docker.sock:/var/run/docker.sock" | sudo tee --append instance/config/che/che.properties

# Restart the Eclipse Che server
docker run -it --rm -v /var/run/docker.sock:/var/run/docker.sock -v /home/ubuntu/:/data -e CHE_HOST="$IP" -e CHE_DOCKER_IP_EXTERNAL="$IP" eclipse/che restart
```

## Step 3: Set docker unix socket permissions
Suffcient permissions are needed so the docker command inside a Eclipse Che workspace can be executed without `sudo`. This is needed for the tengu-cli tool used in the demo.
```
juju ssh eclipse-che/0

sudo chmod 666 /var/run/docker.sock

```

## Step 4: Create the Eclipse Che workspace
Open the Eclipse Che dashboard which should be running on port 8080.
Create a stack based on the [che-tengu-python](https://hub.docker.com/r/sborny/che-tengu-python/) image.
Modify the dev-machine source property to `sborny/che-tengu-python`. Configure the amount of ram the workspace will be allowed to use. If you did not modify the bundle the machine should have 4G in total available, 1.5G should be enough but you can configure this as needed. 

The recipse should look like this:
```
services:
 dev-machine:
  image: sborny/che-tengu-python
```
Save the stack and create a workspace based on the newly created stack. 

## Step 5: Use Eclipse Che to create a project and deploy it to Kubernetes
A dummy project is available in helloflask. This project sets up a very small Api with only one endpoint, namely `/ping`. If all is well, sending a GET request to this endpoint will result in a `pong` response.

The [tengu-cli](https://github.com/tengu-team/tengu-cli/tree/no-kubectl) is used to send deployment requests to an API running in Kubernetes. Assuming you are in the `/projects` directory and names the project `helloflask`, you can use the cli like this:
```
# Log into docker
docker login

# Replace the DOCKER_USERNAME with your own docker id and the WORKSPACE_NAME with the name of your workspace
# The namespace parameter specifies the Kubernetes namespace where the deployment should take place. default is always available on a Kubernetes cluster

tengu deploy --path=./helloflask --workspace="WORKSPACE_NAME" --namespace="default" --docker-repository="DOCKER_USERNAME/helloflask"
```
After the command finished, a tengu folder appears in the project. This contains the generated Kubernetes deployment configuration. It is this configuration which is run by the deployer API running inside Kubernetes. 

## Step 6: View the deployments in Kubernetes
To view all deployments and as a final check that all went well, we can check the status of the cluster via the dashboard. Follow the [instructions](https://github.com/juju-solutions/bundle-canonical-kubernetes/tree/master/fragments/k8s/cdk#interacting-with-the-kubernetes-cluster) to set up kubectl. 

When kubectl is up and running use it to port forward to the dashboard.
```
kubectl proxy
```
Then navigate to `http://localhost:8001/api/v1/namespaces/kube-system/services/kubernetes-dashboard/proxy/`. A deployment with the workspace name should active and running in the cluster.
