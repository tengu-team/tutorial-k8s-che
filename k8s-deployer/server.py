import os
import sys
import json
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from flask import Flask, request, abort, Response, jsonify
from juju import loop
from juju.model import Model
from juju.client.connection import Connection
from juju.client.client import ClientFacade

app = Flask(__name__)
config.load_incluster_config()  # USE WHEN RUNNING IN KUBERNETES POD
# config.load_kube_config() # For local testing


@app.route('/deploy/<workspace>', methods=['PUT'])
def deploy(workspace):
    print("Received deploy request for workspace: " + workspace)
    if not request.get_json():
        print("No JSON payload found")
        sys.stdout.flush()
        abort(400)
    deployment = request.get_json()
    print("Deployment info:")
    print(deployment)
    sys.stdout.flush()
    deployment['metadata']['name'] = workspace
    namespace = deployment['metadata']['namespace'] if 'namespace' in deployment['metadata'] else "default"
    success = False
    print("Checking if deployment exists...")
    sys.stdout.flush()
    if deployment_exists(workspace, namespace):
        print("Deployment EXISTS, replacing...")
        sys.stdout.flush()
        success = replace_deployment(deployment, namespace, workspace)
    else:
        print("No deployment found for workspace " + workspace + ", creating...")
        sys.stdout.flush()
        success = create_deployment(deployment, namespace)
    if not success:
        print("Error creating deployment")
        sys.stdout.flush()
        abort(500)
    print("Done")
    sys.stdout.flush()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/undeploy/<workspace>', methods=['DELETE'])
def undeploy(workspace):
    if not request.get_json():
        abort(400)
    deployment = request.get_json()
    namespace = deployment['metadata']['namespace'] if 'namespace' in deployment['metadata'] else "default"
    body = client.V1DeleteOptions()
    # Set background cascading deletion
    # https://kubernetes.io/docs/concepts/workloads/controllers/garbage-collection/#background-cascading-deletion
    body.propagation_policy = 'Background'
    api_instance = client.ExtensionsV1beta1Api()
    try:
        resp = api_instance.delete_namespaced_deployment(
            name=workspace, body=body, namespace=namespace, grace_period_seconds=0)
        print(resp)
    except ApiException as e:
        print(e)
        abort(500)
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/juju/applications', methods=['GET'])
def get_applications():
    status = loop.run(get_juju_model_status())
    apps = status.applications
    app_info = {}
    for app in apps:
        app_info[app] = {}
        if 'units' in apps[app] and apps[app]['units']:
            for unit in apps[app]['units']:
                app_info[app][unit] = {}
                app_info[app][unit]['ip'] = apps[app]['units'][unit]['public-address']
                app_info[app][unit]['ports'] = apps[app]['units'][unit]['opened-ports']
    return json.dumps(app_info), 200, {'ContentType': 'application/json'}


@app.route('/ping', methods=['GET'])
def ping():
    resp = Response("pong")
    return resp


def deployment_exists(deployment, namespace):
    api_instance = client.AppsV1beta1Api()
    try:
        resp = api_instance.read_namespaced_deployment(deployment, namespace)
        print("Deployment EXISTS")
        return True
    except ApiException as e:
        print("Deployment DOES NOT EXIST")
        return False


def create_deployment(deployment, namespace):
    # api_instance = client.ExtensionsV1beta1Api()
    api_instance = client.AppsV1beta1Api()
    try:
        resp = api_instance.create_namespaced_deployment(
            body=deployment, namespace=namespace)
        print("Deployment created. status='%s'" % str(resp.status))
        return True
    except ApiException as e:
        print(e)
        return False


def replace_deployment(deployment, namespace, workspace):
    api_instance = client.ExtensionsV1beta1Api()
    try:
        resp = api_instance.replace_namespaced_deployment(
            workspace, namespace, body=deployment)
        print("Deployment replaced. status='%s'" % str(resp.status))
        return True
    except ApiException as e:
        print(e)
        return False


async def get_juju_model_status():
    conn = await Connection.connect(os.environ['controller_ip'],
                       os.environ['model_uuid'],
                       os.environ['user'],
                       os.environ['password'],
                       None,)
    client = ClientFacade.from_connection(conn)
    status = await client.FullStatus(None)
    await conn.close()
    return status


if __name__ == "__main__":
    app.run(host='0.0.0.0')
