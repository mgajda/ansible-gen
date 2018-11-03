import docker
import boto3
import json
import sys
import base64

def build_and_ecr_push(version_number, aws_id, image_name, build_image):

    docker_api = docker.APIClient()
    if build_image: 
    	local_tag = image_name
    	print "Building image " + local_tag
    	for line in docker_api.build(path='.', tag=local_tag, dockerfile='./Dockerfile'):
        	process_docker_api_line(line)
    if aws_id is not None:
	print "Push image to ECR.."
    
    	# The ECR Repository URI
    	repo = aws_id + '.dkr.ecr.eu-west-1.amazonaws.com/' + image_name
    	profile = "default"
    	region = "eu-west-1"

    	session = boto3.Session(profile_name=profile, region_name=region)
    	ecr = session.client('ecr')

    	# Make auth call and parse out results
    	auth = ecr.get_authorization_token()
    	token = auth["authorizationData"][0]["authorizationToken"]
    	username, password = base64.b64decode(token).split(':')
    	endpoint = auth["authorizationData"][0]["proxyEndpoint"]

    	auth_config_payload = {'username': username, 'password': password}

    	repo_tag = repo + ':' + str(version_number)

    	print "Tagging latest " + latest_tag
    	if docker_api.tag(image_name, repo) is False:
        	raise RuntimeError("Tag appeared to fail: " + latest_tag)

    	print "Pushing to repo " + latest_tag
    	for line in docker_api.push(repo_tag, stream=True, auth_config=auth_config_payload):
        	process_docker_api_line(line)

    print "Removing taged deployment images"
    docker_api.remove_image(repo_tag, force=True)

def process_docker_api_line(payload):
    """ Process the output from API stream """
    for segment in payload.split('\n'):
        line = segment.strip()
        if line:
            try:
                line_payload = json.loads(line)
            except ValueError as ex:
                print "Could not decipher payload from API: " + ex.message
            if line_payload:
                if "errorDetail" in line_payload:
                    error = line_payload["errorDetail"]
                    sys.stderr.write(error["message"])
                    raise RuntimeError("Error on build - code " + `error["code"]`)
                elif "stream" in line_payload:
                    sys.stdout.write(line_payload["stream"])

