# k8s-deployer


This image sets up an API to create / destroy deployments on a Kubernetes cluster and gives access to the Juju model in which the Kubernetes cluster is deployed.
The image can only run inside a Kubernetes cluster. And is deployed via the [kubernetes-api](https://github.com/tengu-team/tutorial-k8s-che/tree/master/xenial/kubernetes-api) charm.


The following endpoints are defined:

```
/deploy/<workspace>
	PUT
	Requires a json payload with a valid Kubernetes deployment configuration. Only one deployment can be active per workspace.
/undeploy/<workspace>
	DELETE
	Removes a deployment for a workspace.
/juju/applications
	GET
	Returns info about all deployed juju charms in the current model.
/ping
	GET
	Returns 'pong' on success
```
