import base64
import json
import os
import shutil
from cfn_tools import load_yaml
import cfn_flip.yaml_dumper
import yaml
from datetime import datetime

import boto3
import botocore
import docker

BASE_ECR_URL = '288687564189.dkr.ecr.eu-west-2.amazonaws.com/'
ECR_NAME = 'doa-composition'


# deploys infrastructure resoures in AWS
def deploy_resources(resources_template_path, rabbitmq_credentials_path):
    # reading aws credentials
    aws_credentials = _read_aws_credentials('')
    access_key_id = aws_credentials['access_key_id']
    secret_access_key = aws_credentials['secret_access_key']
    aws_region = aws_credentials['region']
    # creating cloud formation client
    cloud_client = boto3.client('cloudformation', aws_access_key_id=access_key_id,
                                aws_secret_access_key=secret_access_key, region_name=aws_region)
    # reading resources template
    resources_template = _parse_template(cloud_client, resources_template_path)
    # creating resources stack
    external_url = ''
    rabbitmq_url = ''
    res = _create_stack(cloud_client, resources_template, 'doa-resources')
    stacks = res['Stacks']
    for stack in stacks:
        if stack['StackName'] == 'doa-resources':
            outputs = stack['Outputs']
            for output in outputs:
                if output['OutputKey'] == 'ExternalUrl':
                    external_url = output['OutputValue']
                if output['OutputKey'] == 'AmqpEndpoints':
                    rabbitmq_url = output['OutputValue']
    _update_rabbitmq_credentials(rabbitmq_url, rabbitmq_credentials_path)
    return external_url, rabbitmq_url


# removes infrastructure resources in AWS
def remove_resources():
    # reading aws credentials
    aws_credentials = _read_aws_credentials('')
    access_key_id = aws_credentials['access_key_id']
    secret_access_key = aws_credentials['secret_access_key']
    aws_region = aws_credentials['region']
    # creating cloud formation client
    cloud_client = boto3.client('cloudformation', aws_access_key_id=access_key_id,
                                aws_secret_access_key=secret_access_key, region_name=aws_region)
    _remove_stack(cloud_client, 'doa-resources')


# deploys services in AWS
def deploy_services(service_template_path, services):
    # reading aws credentials
    aws_credentials = _read_aws_credentials('')
    access_key_id = aws_credentials['access_key_id']
    secret_access_key = aws_credentials['secret_access_key']
    aws_region = aws_credentials['region']
    # creating cloud formation client
    cloud_client = boto3.client('cloudformation', aws_access_key_id=access_key_id,
                                aws_secret_access_key=secret_access_key, region_name=aws_region)
    # for each service push image and create stack
    for service in services:
        print('Creating stack for service ' + service['name'] + '...')
        shutil.copyfile('./dockers/' + service['name'].replace('_', '-'), './Dockerfile')
        # pushing image for service
        service = _push_docker_image('.', service, aws_credentials)
        # reading service template
        service_path, stack_name = _create_service_template(service_template_path, service)
        service_template = _parse_template(cloud_client, service_path)
        # creating service stack
        res = _create_stack(cloud_client, service_template, stack_name)
        print('Stack created for service ' + service['name'] + '...')
        os.remove(service_path)


# removes services from AWS
def remove_services(services):
    # reading aws credentials
    aws_credentials = _read_aws_credentials('')
    access_key_id = aws_credentials['access_key_id']
    secret_access_key = aws_credentials['secret_access_key']
    aws_region = aws_credentials['region']
    # creating cloud formation client
    cloud_client = boto3.client('cloudformation', aws_access_key_id=access_key_id,
                                aws_secret_access_key=secret_access_key, region_name=aws_region)
    for service in services:
        _remove_stack(cloud_client, service['name'].replace('_', '-') + '-stack')


# reads aws credentials from file or environment variables
def _read_aws_credentials(filename):
    try:
        with open(filename) as json_data:
            credentials = json.load(json_data)

        for variable in ('access_key_id', 'secret_access_key', 'region'):
            if variable not in credentials.keys():
                msg = '"{}" cannot be found in {}'.format(variable, filename)
                raise KeyError(msg)

    except FileNotFoundError:
        try:
            credentials = {
                'access_key_id': os.environ['AWS_ACCESS_KEY_ID'],
                'secret_access_key': os.environ['AWS_SECRET_ACCESS_KEY'],
                'region': os.environ['AWS_REGION']
            }
        except KeyError:
            msg = 'no AWS credentials found in file or environment variables'
            raise RuntimeError(msg)

    return credentials


# create a stack template file for a service
def _create_service_template(service_template_path, service):
    with open(service_template_path, 'r') as stream:
        service_template = load_yaml(stream)
        stack_name = service['name'].replace('_','-') + '-stack'
        # customising service template
        service_template['Description'] = 'Deploy service ' + service['name'] + ' on AWS Fargate, hosted in a private subnet, but accessible via a public balancer'
        service_template['Parameters']['StackName']['Default'] = stack_name
        service_template['Parameters']['ServiceName']['Default'] = service['name'].replace('_','')
        service_template['Parameters']['ImageUrl']['Default'] = service['imageUrl']
        service_template['Parameters']['ContainerPort']['Default'] = service['port']
        service_template['Parameters']['ContainerCpu']['Default'] = service['cpu']
        service_template['Parameters']['ContainerMemory']['Default'] = service['memory']
        service_template['Parameters']['Path']['Default'] = service['path']
        service_template['Parameters']['Priority']['Default'] = service['priority']
        service_template['Parameters']['DesiredCount']['Default'] = service['count']
        service_path = service['name'] + '-template.yml'
        with open(service_path, 'w') as f:
            dumper = cfn_flip.yaml_dumper.get_dumper(clean_up=False, long_form=False)
            raw = yaml.dump(
                service_template,
                Dumper=dumper,
                default_flow_style=False,
                allow_unicode=True
            )
            f.write(raw)
        return service_path, stack_name


# parse a stack template
def _parse_template(cloud_client, template_path):
    with open(template_path) as template_fileobj:
        template_data = template_fileobj.read()
    cloud_client.validate_template(TemplateBody=template_data)
    return template_data


# create stack in aws
def _create_stack(cloud_client, template_body, stack_name):
    res = {}
    params = {
        'StackName': stack_name,
        'TemplateBody': template_body,
    }
    try:
        exists, stack_id = _stack_exists(cloud_client, stack_name)
        if exists:
            print('Updating stack ' + stack_name + '...')
            res = cloud_client.describe_stacks(StackName=stack_id)
            stack_result = cloud_client.update_stack(**params, Capabilities=['CAPABILITY_IAM'])
            waiter = cloud_client.get_waiter('stack_update_complete')
        else:
            print('Creating stack ' + stack_name + '...')
            stack_result = cloud_client.create_stack(**params, Capabilities=['CAPABILITY_IAM'])
            waiter = cloud_client.get_waiter('stack_create_complete')
        print("... waiting for stack to be ready...")
        waiter.wait(StackName=stack_name)
    except botocore.exceptions.ClientError as ex:
        error_message = ex.response['Error']['Message']
        if error_message == 'No updates are to be performed.':
            print('No changes...')
        else:
            raise
    else:
        res = cloud_client.describe_stacks(StackName=stack_result['StackId'])
    return res


# removes stack from AWS
def _remove_stack(cloud_client, stack_name):
    try:
        exists, stack_id = _stack_exists(cloud_client, stack_name)
        if exists:
            print('Deleting stack ' + stack_name + '...')
            cloud_client.delete_stack(StackName=stack_name)
        else:
            print('Stack ' + stack_name + ' does not exist...')
    except:
        print('Exception removing stack: ' + stack_name + '...')


# validate if stack exists in AWS
def _stack_exists(cloud_client, stack_name):
    stacks = cloud_client.list_stacks()['StackSummaries']
    for stack in stacks:
        if stack['StackStatus'] == 'DELETE_COMPLETE':
            continue
        if stack_name == stack['StackName']:
            return True, stack['StackId']
    return False, -1


# json serialiser
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type not serializable")


# builds docker image and push the image to AWS ECR
def _push_docker_image(path, service, aws_credentials):
    service_tag = service['name']
    service_name = service['name']
    access_key_id = aws_credentials['access_key_id']
    secret_access_key = aws_credentials['secret_access_key']
    aws_region = aws_credentials['region']

    # build Docker image
    docker_client = docker.from_env()
    print('*** Registering Service: ' + service_name + ' ***')
    image, build_log = docker_client.images.build(path=path, tag=service_name, rm=True)
    print('The image was built...')

    # get AWS ECR login token
    ecr_client = boto3.client('ecr', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key,
                              region_name=aws_region)

    print('ECR client authenticated...')
    ecr_credentials = (ecr_client.get_authorization_token()['authorizationData'][0])
    ecr_username = 'AWS'
    ecr_password = (base64.b64decode(ecr_credentials['authorizationToken']).replace(b'AWS:', b'').decode('utf-8'))
    ecr_url = ecr_credentials['proxyEndpoint']
    # get Docker to login/authenticate with ECR
    docker_client.login(username=ecr_username, password=ecr_password, registry=ecr_url)
    print('Docker client authenticated with ECR...')
    # tag image for AWS ECR
    ecr_repo_name = '{}/{}'.format(ecr_url.replace('https://', ''), ECR_NAME)
    print(ecr_repo_name)
    image.tag(ecr_repo_name, tag=service_name)
    print('Image tagged for AWS ECR: ' + service_name + '...')

    # push image to AWS ECR
    push_log = docker_client.images.push(ecr_repo_name, tag=service_name)
    # print(push_log)
    print('Image pushed to AWS ECR: ' + service_name + '...')
    service['imageUrl'] = BASE_ECR_URL + ECR_NAME + ':' + service_name
    return service


# updates rabbitmq credentials file with the url of the created broker
def _update_rabbitmq_credentials(rabbitmq_url, rabbitmq_credentials_path):
    with open(rabbitmq_credentials_path, 'r') as stream:
        rabbitmq_credentials = load_yaml(stream)
        rabbitmq_credentials['rabbitmq_url'] = rabbitmq_url.split(':')[1].replace('//','')
    with open(rabbitmq_credentials_path, 'w') as f:
             dumper = cfn_flip.yaml_dumper.get_dumper(clean_up=False, long_form=False)
             raw = yaml.dump(
                 rabbitmq_credentials,
                 Dumper=dumper,
                 default_flow_style=False,
                 allow_unicode=True
             )
             f.write(raw)
